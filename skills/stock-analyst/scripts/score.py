#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yfinance>=0.2.40", "pandas>=2.0"]
# ///
"""Quick multi-factor score for one or more tickers, using Yahoo Finance data.

Usage:
    uv run score.py AAPL
    uv run score.py AAPL MSFT RELIANCE.NS --json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from common import benchmark_for, import_yfinance, load_config
from scoring import classify_asset, compute, is_fund

yf = import_yfinance()


def _num(info: dict, key: str):
    v = info.get(key)
    return float(v) if isinstance(v, (int, float)) else None


def _rsi(close, period: int = 14) -> float | None:
    if len(close) <= period:
        return None
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False).mean()
    if loss.iloc[-1] == 0:
        return 100.0
    return float(100 - 100 / (1 + gain.iloc[-1] / loss.iloc[-1]))


def _return(close, days: int):
    return float(close.iloc[-1] / close.iloc[-days] - 1) if len(close) > days else None


def fetch(ticker: str) -> dict:
    """Collect everything the scorer needs. Gaps are recorded in `notes`, not hidden."""
    notes = []
    t = yf.Ticker(ticker)
    # Yahoo can return a trailing row with no close (e.g. Indian stocks mid-session); drop it.
    close = t.history(period="1y", auto_adjust=True)["Close"].dropna()
    if close.empty:
        raise LookupError(
            f"No price history for {ticker!r}. Check the symbol "
            "(Indian stocks need .NS or .BO, e.g. RELIANCE.NS; crypto needs -USD)."
        )
    try:
        info = t.info or {}
    except Exception as e:  # Yahoo sometimes rate-limits the info endpoint
        info = {}
        notes.append(f"Company info unavailable ({e}); fundamentals skipped")

    price = float(close.iloc[-1])
    m = {
        "ticker": ticker.upper(),
        "name": info.get("shortName") or info.get("longName") or ticker.upper(),
        "currency": info.get("currency", ""),
        "price": price,
        "high_52w": float(close.max()),
        "low_52w": float(close.min()),
        "drawdown": price / float(close.max()) - 1,
        "volatility_1y": float(close.pct_change().std() * 252 ** 0.5) if len(close) > 20 else None,
        "ma50": float(close.tail(50).mean()) if len(close) >= 50 else None,
        "ma200": float(close.tail(200).mean()) if len(close) >= 200 else None,
        "rsi": _rsi(close),
        "return_6m": _return(close, 126),
    }
    if is_fund(info.get("quoteType"), m["name"]):
        m.update(_fund_metrics(t, info, price, notes))
    else:
        m.update(_stock_metrics(t, info, notes))

    bench = benchmark_for(ticker, m.get("asset_class"))
    m["benchmark"] = bench
    if bench:
        bench_close = yf.Ticker(bench).history(period="1y", auto_adjust=True)["Close"].dropna()
        if bench_close.empty:
            notes.append(f"Benchmark {bench} unavailable; relative strength skipped")
        else:
            m["bench_return_6m"] = _return(bench_close, 126)

    m["notes"] = notes
    return m


def _fund_metrics(t, info: dict, price: float, notes: list) -> dict:
    """ETF data: cost, size, track record. Indian ETFs have none of this on Yahoo."""
    er = _num(info, "netExpenseRatio")
    out = {
        "asset_type": "etf",
        "asset_class": classify_asset(info.get("category"), info.get("shortName") or info.get("longName")),
        "category": info.get("category"),
        "fund_family": info.get("fundFamily"),
        "expense_ratio": er / 100 if er is not None else None,  # Yahoo reports a percentage
        "aum": _num(info, "totalAssets"),
        "yield": _num(info, "yield"),
        "return_3y": _num(info, "threeYearAverageReturn"),
        "return_5y": _num(info, "fiveYearAverageReturn"),
    }
    nav = _num(info, "navPrice")
    out["premium"] = price / nav - 1 if nav else None
    try:
        ops = t.funds_data.fund_operations
        row = "Annual Report Expense Ratio"
        if ops is not None and row in ops.index:
            own, cat = ops.loc[row].iloc[0], ops.loc[row].get("Category Average")
            if out["expense_ratio"] is None and own:
                out["expense_ratio"] = float(own)
            out["category_expense_ratio"] = float(cat) if cat else None
    except Exception as e:
        if out["expense_ratio"] is not None or out["aum"] is not None:
            notes.append(f"Fund details partly unavailable ({type(e).__name__}); category comparison skipped")
    if out["expense_ratio"] is None and out["aum"] is None:
        notes.append("No fund data on Yahoo (common for Indian ETFs); check the expense ratio on the fund's site")
    return out


def _stock_metrics(t, info: dict, notes: list) -> dict:
    de = _num(info, "debtToEquity")
    m = {
        "asset_type": "stock",
        "sector": info.get("sector"),
        "trailing_pe": _num(info, "trailingPE"),
        "forward_pe": _num(info, "forwardPE"),
        "peg": _num(info, "trailingPegRatio") or _num(info, "pegRatio"),
        "revenue_growth": _num(info, "revenueGrowth"),
        "earnings_growth": _num(info, "earningsGrowth"),
        "profit_margin": _num(info, "profitMargins"),
        "roe": _num(info, "returnOnEquity"),
        "debt_to_equity": de / 100 if de is not None else None,  # Yahoo reports a percentage
        "current_ratio": _num(info, "currentRatio"),
        "free_cash_flow": _num(info, "freeCashflow"),
        "recommendation_mean": _num(info, "recommendationMean"),
        "target_price": _num(info, "targetMeanPrice"),
        "analyst_count": info.get("numberOfAnalystOpinions") or 0,
        "market_cap": _num(info, "marketCap"),
    }

    try:
        eh = t.earnings_history
        if eh is not None and not eh.empty and "surprisePercent" in eh:
            m["eps_surprises"] = [float(x) for x in eh["surprisePercent"].dropna().tail(4)]
    except Exception as e:
        notes.append(f"Earnings history unavailable ({type(e).__name__}); earnings factor skipped")

    try:
        cal = t.calendar or {}
        dates = cal.get("Earnings Date") if isinstance(cal, dict) else None
        if dates:
            upcoming = [d for d in dates if d >= date.today()]
            if upcoming:
                m["next_earnings"] = upcoming[0].isoformat()
                m["days_to_earnings"] = (upcoming[0] - date.today()).days
    except Exception as e:
        notes.append(f"Earnings calendar unavailable ({type(e).__name__})")
    return m


def _bar(v) -> str:
    if v is None:
        return "   n/a"
    filled = round((v + 1) * 5)  # -1..1 -> 0..10
    return f"{v:+.2f} " + "█" * filled + "·" * (10 - filled)


def _fmt(v, kind: str = "num") -> str:
    if v is None:
        return "n/a"
    if kind == "pct":
        return f"{v * 100:.1f}%"
    if kind == "pct2":
        return f"{v * 100:.2f}%"
    return f"{v:,.2f}"


def render(m: dict, r: dict) -> str:
    lines = [
        f"{m['name']} ({m['ticker']}) · {m['currency']} {m['price']:,.2f} · as of {date.today()}",
        f"Score {r['composite']:+.0f}/100 → {r['verdict']}  (confidence {r['confidence']}, data coverage {r['coverage']:.0%})",
        "",
        "Factors:",
    ]
    lines += [f"  {k:<14}{_bar(v)}" for k, v in r["factors"].items()]
    lines += ["", "Key numbers:"]
    if m.get("asset_type") == "etf":
        lines += _etf_numbers(m)
    else:
        lines += _stock_numbers(m)
    lines.append(
        "  Judged against: " + (m["benchmark"] if m.get("benchmark") else "none (absolute return)")
        + f"  → log with --benchmark {m.get('benchmark') or 'none'}"
    )
    if r["flags"]:
        lines += ["", "Flags:"] + [f"  ⚠ {f}" for f in r["flags"]]
    if m["notes"]:
        lines += ["", "Data gaps:"] + [f"  - {n}" for n in m["notes"]]
    return "\n".join(lines)


def _price_numbers(m: dict) -> list[str]:
    return [
        f"  RSI {_fmt(m['rsi'])} · 50d MA {_fmt(m['ma50'])} · 200d MA {_fmt(m['ma200'])}",
        f"  52w range {_fmt(m['low_52w'])} – {_fmt(m['high_52w'])} ({_fmt(m['drawdown'], 'pct')} from high)"
        f" · 6m return {_fmt(m['return_6m'], 'pct')}"
        + (f" vs {m['benchmark']} {_fmt(m['bench_return_6m'], 'pct')}" if m.get("bench_return_6m") is not None else ""),
    ]


def _etf_numbers(m: dict) -> list[str]:
    aum = m.get("aum")
    return [
        f"  Fund: {m.get('category') or 'category n/a'} · asset class {m['asset_class']}"
        + (f" · {m['fund_family']}" if m.get("fund_family") else ""),
        f"  Expense ratio {_fmt(m.get('expense_ratio'), 'pct2')}"
        f" (category avg {_fmt(m.get('category_expense_ratio'), 'pct2')})"
        f" · assets {f'{aum / 1e9:,.1f}B' if aum else 'n/a'} · yield {_fmt(m.get('yield'), 'pct')}",
        f"  Avg yearly return 3y {_fmt(m.get('return_3y'), 'pct')} · 5y {_fmt(m.get('return_5y'), 'pct')}"
        f" · volatility {_fmt(m.get('volatility_1y'), 'pct')} · vs NAV {_fmt(m.get('premium'), 'pct')}",
    ] + _price_numbers(m)


def _stock_numbers(m: dict) -> list[str]:
    lines = [
        f"  P/E trailing {_fmt(m['trailing_pe'])} · forward {_fmt(m['forward_pe'])} · PEG {_fmt(m['peg'])}",
        f"  Revenue growth {_fmt(m['revenue_growth'], 'pct')} · earnings growth {_fmt(m['earnings_growth'], 'pct')}",
        f"  Margin {_fmt(m['profit_margin'], 'pct')} · ROE {_fmt(m['roe'], 'pct')} · debt/equity {_fmt(m['debt_to_equity'])}",
    ] + _price_numbers(m) + [
        f"  Analysts: {m['analyst_count']} · rating {_fmt(m['recommendation_mean'])} (1=strong buy) · target {_fmt(m['target_price'])}",
    ]
    if m.get("next_earnings"):
        lines.append(f"  Next earnings: {m['next_earnings']}")
    return lines


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("tickers", nargs="+", help="Yahoo Finance symbols, e.g. AAPL, RELIANCE.NS, BTC-USD")
    p.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = p.parse_args()

    cfg = load_config()
    results, failed = [], 0
    for ticker in args.tickers:
        try:
            m = fetch(ticker)
        except Exception as e:
            print(f"✗ {ticker}: {e}", file=sys.stderr)
            failed += 1
            continue
        results.append((m, compute(m, cfg)))

    if args.json:
        print(json.dumps([{"metrics": m, "result": r} for m, r in results], indent=2, default=str))
    else:
        print("\n\n".join(render(m, r) for m, r in results))
        if len(results) > 1:
            print("\nRanking: " + " > ".join(
                f"{m['ticker']} ({r['composite']:+.0f})"
                for m, r in sorted(results, key=lambda x: -x[1]["composite"])
            ))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
