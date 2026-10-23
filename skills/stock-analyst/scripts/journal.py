#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yfinance>=0.2.40", "pandas>=2.0"]
# ///
"""Journal of every stock call, so past calls can be checked against what happened.

Usage:
    uv run journal.py add AAPL --price 230.5 --verdict BUY-lean --score 32 --thesis "AI cycle + buybacks"
    uv run journal.py list [AAPL]
    uv run journal.py review [--min-age-days 30]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from common import DATA_DIR, benchmark_for, import_yfinance, latest_prices, load_config

JOURNAL = DATA_DIR / "journal.jsonl"


def load() -> list[dict]:
    if not JOURNAL.exists():
        return []
    return [json.loads(line) for line in JOURNAL.read_text().splitlines() if line.strip()]


def append(entry: dict) -> None:
    JOURNAL.parent.mkdir(parents=True, exist_ok=True)
    with JOURNAL.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def judge(verdict: str, ret: float, bench_ret: float | None, band: float = 0.03) -> str:
    """Was the call right? Compares the stock's return with the benchmark's.

    BUY is right if it beat the benchmark, SELL if it lagged it, HOLD if it stayed
    within `band` of it. Without a benchmark, the raw return is used.
    """
    excess = ret - (bench_ret or 0.0)
    v = verdict.upper()
    if v.startswith("BUY"):
        return "right" if excess > 0 else "wrong"
    if v.startswith("SELL"):
        return "right" if excess < 0 else "wrong"
    return "right" if abs(excess) <= band else "wrong"


def cmd_add(a) -> None:
    entry = {
        "id": f"{date.today().isoformat()}-{a.ticker.upper()}-{len(load()) + 1}",
        "date": date.today().isoformat(),
        "ticker": a.ticker.upper(),
        "price": a.price,
        "verdict": a.verdict,
        "score": a.score,
        "target": a.target,
        "source": a.source,
        "thesis": a.thesis,
        "benchmark": benchmark_for(a.ticker),
    }
    append(entry)
    print(f"Logged {entry['id']}: {entry['verdict']} @ {entry['price']}")


def cmd_list(a) -> None:
    rows = [e for e in load() if not a.ticker or e["ticker"] == a.ticker.upper()]
    if not rows:
        print("No journal entries yet." if not a.ticker else f"No entries for {a.ticker.upper()}.")
        return
    for e in rows:
        score = f" score {e['score']:+.0f}" if e.get("score") is not None else ""
        print(f"{e['date']}  {e['ticker']:<12} {e['verdict']:<24} @ {e['price']:<10}{score}  {e.get('thesis') or ''}")


def cmd_review(a) -> None:
    min_age = a.min_age_days if a.min_age_days is not None else load_config()["review"]["min_age_days"]
    today = date.today()
    due = [e for e in load() if (today - date.fromisoformat(e["date"])).days >= min_age]
    if not due:
        print(f"No calls older than {min_age} days to review yet.")
        return

    yf = import_yfinance()
    prices = latest_prices(sorted({e["ticker"] for e in due}))
    right = 0
    print(f"{'date':<11}{'ticker':<12}{'call':<24}{'return':>8}{'bench':>8}  outcome")
    for e in due:
        ret = prices[e["ticker"]] / e["price"] - 1
        bh = yf.Ticker(e["benchmark"]).history(start=e["date"], auto_adjust=True)
        bench_ret = float(bh["Close"].iloc[-1] / bh["Close"].iloc[0] - 1) if not bh.empty else None
        outcome = judge(e["verdict"], ret, bench_ret)
        right += outcome == "right"
        b = f"{bench_ret * 100:+.1f}%" if bench_ret is not None else "n/a"
        print(f"{e['date']:<11}{e['ticker']:<12}{e['verdict']:<24}{ret * 100:+7.1f}%{b:>8}  {outcome}")
    print(f"\nHit rate: {right}/{len(due)} ({right / len(due):.0%})")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("add", help="log a call")
    s.add_argument("ticker")
    s.add_argument("--price", type=float, required=True)
    s.add_argument("--verdict", required=True, help="e.g. BUY-lean, HOLD, SELL-lean")
    s.add_argument("--score", type=float)
    s.add_argument("--target", type=float, help="price target, if any")
    s.add_argument("--source", default="quick", choices=["quick", "report", "comparison"])
    s.add_argument("--thesis", default="", help="one line: why")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("list", help="show past calls")
    s.add_argument("ticker", nargs="?")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("review", help="check old calls against what the price did since")
    s.add_argument("--min-age-days", type=int)
    s.set_defaults(fn=cmd_review)

    a = p.parse_args()
    a.fn(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
