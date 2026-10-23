#!/usr/bin/env python3
"""Check whether the skills this one borrows from have changed upstream.

Compares the GitHub blob SHA of each tracked file with the SHA recorded in
sources.json. Stdlib only. Never modifies files; it reports what changed.

Usage:
    python3 check_upstream.py            # report changes
    python3 check_upstream.py --accept   # record current upstream SHAs as reviewed
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

SOURCES = Path(__file__).resolve().parent.parent / "sources.json"


def upstream_sha(repo: str, path: str) -> str:
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)["sha"]


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--accept", action="store_true", help="mark current upstream versions as reviewed")
    a = p.parse_args()

    sources = json.loads(SOURCES.read_text())
    changed, errors = [], []
    for src in sources["sources"]:
        for f in src["files"]:
            try:
                sha = upstream_sha(src["repo"], f["path"])
            except Exception as e:
                errors.append(f"{src['repo']}/{f['path']}: {e}")
                continue
            if sha != f["sha"]:
                changed.append((src, f, sha))

    for src, f, sha in changed:
        print(f"CHANGED  {src['repo']}/{f['path']}")
        print(f"         use: {src['use']}")
        print(f"         view: https://github.com/{src['repo']}/blob/HEAD/{f['path']}")
        if a.accept:
            f["sha"] = sha
    if not changed:
        print("All tracked upstream files are unchanged.")
    for e in errors:
        print(f"ERROR    {e} (GitHub may be rate-limiting; try again later)", file=sys.stderr)
    if a.accept and changed:
        SOURCES.write_text(json.dumps(sources, indent=2) + "\n")
        print(f"Recorded {len(changed)} new SHA(s) in sources.json")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
