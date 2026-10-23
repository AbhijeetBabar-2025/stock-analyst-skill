#!/usr/bin/env python3
"""Check the dashboard's third-party CDN files.

For every <link>/<script> in the dashboard page with an integrity hash:
  - fails if the file the CDN serves no longer matches the hash (tampered, or the
    URL changed), since browsers would then refuse to load it;
  - warns if a newer version of the package exists on npm, so it can be updated.

Stdlib only. Usage: python3 .github/scripts/check_cdn.py [path/to/index.html]
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import sys
import urllib.request
from pathlib import Path

PAGE = Path(sys.argv[1] if len(sys.argv) > 1 else "skills/stock-analyst/web/index.html")
TAG = re.compile(r'<(?:link|script)\b[^>]*?(?:href|src)="(https://[^"]+)"[^>]*?integrity="(sha\d{3})-([^"]+)"', re.S)
PKG = re.compile(r"/npm/((?:@[^/]+/)?[^@/]+)@([^/]+)/")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "stock-analyst-cdn-check"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main() -> int:
    html = PAGE.read_text()
    found = TAG.findall(html)
    unpinned = re.findall(r'<(?:link|script)\b[^>]*?(?:href|src)="(https://[^"]+)"(?![^>]*integrity)[^>]*>', html)
    failures = 0
    for url in unpinned:
        print(f"FAIL  no integrity hash: {url}")
        failures += 1
    for url, algo, expected in found:
        actual = base64.b64encode(hashlib.new(algo, fetch(url)).digest()).decode()
        if actual != expected:
            print(f"FAIL  hash mismatch: {url}\n      expected {expected}\n      got      {actual}")
            failures += 1
        else:
            print(f"ok    {url}")
        m = PKG.search(url)
        if m:
            name, version = m.groups()
            latest = json.loads(fetch(f"https://registry.npmjs.org/{name}/latest"))["version"]
            if latest != version:
                print(f"::warning::{name} {version} is outdated (latest {latest}); update the URL and its integrity hash")
    if not found:
        print(f"FAIL  no pinned CDN files found in {PAGE}")
        failures += 1
    print(f"{len(found)} pinned file(s), {failures} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
