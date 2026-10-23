#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yfinance>=0.2.40", "pandas>=2.0"]
# ///
"""Track holdings and profit/loss. Stored locally in data/portfolio.json.

Usage:
    uv run portfolio.py add AAPL --qty 10 --cost 180
    uv run portfolio.py remove AAPL [--qty 5]
    uv run portfolio.py show
"""

from __future__ import annotations

import argparse
import json
import sys

from common import DATA_DIR, latest_prices

PORTFOLIO = DATA_DIR / "portfolio.json"
CONCENTRATION_LIMIT = 0.30


def load() -> dict:
    return json.loads(PORTFOLIO.read_text()) if PORTFOLIO.exists() else {}


def save(holdings: dict) -> None:
    PORTFOLIO.parent.mkdir(parents=True, exist_ok=True)
    PORTFOLIO.write_text(json.dumps(holdings, indent=2) + "\n")


def add(holdings: dict, ticker: str, qty: float, cost: float) -> dict:
    """Add shares, averaging the cost basis with any existing position."""
    t = ticker.upper()
    old = holdings.get(t, {"qty": 0.0, "avg_cost": 0.0})
    new_qty = old["qty"] + qty
    avg = (old["qty"] * old["avg_cost"] + qty * cost) / new_qty
    holdings[t] = {"qty": new_qty, "avg_cost": round(avg, 4)}
    return holdings


def remove(holdings: dict, ticker: str, qty: float | None) -> dict:
    t = ticker.upper()
    if t not in holdings:
        raise KeyError(f"{t} is not in the portfolio; run `portfolio.py show` to see holdings")
    if qty is None or qty >= holdings[t]["qty"]:
        del holdings[t]
    else:
        holdings[t]["qty"] -= qty
    return holdings


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add")
    s.add_argument("ticker")
    s.add_argument("--qty", type=float, required=True)
    s.add_argument("--cost", type=float, required=True, help="price paid per share")
    s = sub.add_parser("remove")
    s.add_argument("ticker")
    s.add_argument("--qty", type=float, help="omit to remove the whole position")
    sub.add_parser("show")
    a = p.parse_args()

    holdings = load()
    if a.cmd == "add":
        save(add(holdings, a.ticker, a.qty, a.cost))
        h = holdings[a.ticker.upper()]
        print(f"{a.ticker.upper()}: {h['qty']:g} @ avg {h['avg_cost']:,.2f}")
        return 0
    if a.cmd == "remove":
        try:
            save(remove(holdings, a.ticker, a.qty))
        except KeyError as e:
            print(e.args[0], file=sys.stderr)
            return 1
        print(f"Updated {a.ticker.upper()}")
        return 0

    if not holdings:
        print("Portfolio is empty. Add a holding with: portfolio.py add TICKER --qty N --cost PRICE")
        return 0
    prices = latest_prices(list(holdings))
    values = {t: h["qty"] * prices[t] for t, h in holdings.items()}
    total = sum(values.values())
    cost_total = sum(h["qty"] * h["avg_cost"] for h in holdings.values())
    print(f"{'ticker':<12}{'qty':>10}{'avg cost':>12}{'price':>12}{'value':>14}{'P&L':>9}{'weight':>8}")
    for t, h in sorted(holdings.items(), key=lambda kv: -values[kv[0]]):
        pnl = prices[t] / h["avg_cost"] - 1
        w = values[t] / total
        warn = "  ⚠ concentrated" if w > CONCENTRATION_LIMIT else ""
        print(f"{t:<12}{h['qty']:>10g}{h['avg_cost']:>12,.2f}{prices[t]:>12,.2f}{values[t]:>14,.2f}"
              f"{pnl * 100:>8.1f}%{w * 100:>7.1f}%{warn}")
    print(f"\nTotal value {total:,.2f} · cost {cost_total:,.2f} · P&L {(total / cost_total - 1) * 100:+.1f}%")
    print("(Values are in each stock's own currency; totals mix currencies if you hold several markets.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
