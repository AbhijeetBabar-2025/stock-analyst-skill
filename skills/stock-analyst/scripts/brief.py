"""Plain-English brief for one scanned ticker: why it's moving, bull and bear cases,
what to watch, cautions, research gaps and trading-practice notes.

Built only from the scan's numbers (no third-party imports), so it's unit-tested
offline. It can't know the news behind a move; the dashboard shows headlines and
any saved full report next to it.
"""

from __future__ import annotations

BULL_AT = 0.25   # factor scores above this count as a strength
BEAR_AT = -0.25  # and below this as a weakness


def _pct(v, signed=False):
    return f"{v * 100:+.1f}%" if signed else f"{abs(v) * 100:.1f}%"


def _px(v):
    return f"{v:,.2f}"


def _trend(m):
    price, ma50, ma200 = m.get("price"), m.get("ma50"), m.get("ma200")
    if not (price and ma50 and ma200):
        return None, None
    gap = price / ma200 - 1
    if price < ma200 and ma50 < ma200:
        return "down", (f"In a downtrend: the price is {_pct(gap)} below its 200-day average, "
                        f"and the 50-day average is below the 200-day.")
    if price > ma200 and ma50 > ma200:
        return "up", (f"In an uptrend: the price is {_pct(gap)} above its 200-day average, "
                      f"and the 50-day average is above the 200-day.")
    return "mixed", "No clear trend: the price and its 50-day and 200-day averages disagree."


def _why_moving(m, r):
    out = []
    _, line = _trend(m)
    if line:
        out.append(line)
    rets = [(label, m.get(k)) for label, k in (("1 month", "return_1m"), ("3 months", "return_3m"),
                                                ("6 months", "return_6m")) if m.get(k) is not None]
    if rets:
        out.append("Price change: " + ", ".join(
            f"{'up' if v >= 0 else 'down'} {_pct(v)} over {label}" for label, v in rets) + ".")
    rel, bench = m.get("return_6m"), m.get("bench_return_6m")
    if rel is not None and bench is not None and m.get("benchmark"):
        diff = (rel - bench) * 100
        word = "Beating" if diff >= 0 else "Lagging"
        out.append(f"{word} {m['benchmark']} by {abs(diff):.1f} percentage points over 6 months.")
    dd = m.get("drawdown")
    if dd is not None and dd <= -0.10:
        out.append(f"Now {_pct(dd)} below its 52-week high of {_px(m['high_52w'])}.")
    elif dd is not None and dd >= -0.03:
        out.append(f"Trading near its 52-week high of {_px(m['high_52w'])}.")
    rsi = m.get("rsi")
    if rsi is not None:
        if rsi > 70:
            out.append(f"RSI {rsi:.0f}: buying looks stretched (overbought).")
        elif rsi < 30:
            out.append(f"RSI {rsi:.0f}: selling looks stretched (oversold); bounces are common but not guaranteed.")
        elif rsi < 40:
            out.append(f"RSI {rsi:.0f}: close to oversold.")
    days = m.get("days_to_earnings")
    if days is not None and 0 <= days <= 21:
        out.append(f"Earnings due {m.get('next_earnings')} (in {days} days); prices often move ahead of results.")
    surprises = m.get("eps_surprises") or []
    if surprises:
        beats = sum(1 for s in surprises if s > 0)
        out.append(f"Beat profit forecasts in {beats} of the last {len(surprises)} quarters.")
    return out


def _factor_lines(m, positive: bool) -> dict[str, str]:
    """One concrete sentence per factor, phrased as a strength or a weakness."""
    f = {}
    pe = m.get("forward_pe") or m.get("trailing_pe")
    if pe is not None:
        f["valuation"] = (f"Valuation looks reasonable: P/E {pe:.1f}" if positive
                          else f"Valuation is stretched: P/E {pe:.1f}" if pe > 0
                          else "Valuation: the company is losing money (negative P/E)")
        if m.get("peg"):
            f["valuation"] += f", PEG {m['peg']:.2f}."
        else:
            f["valuation"] += "."
    rg, eg = m.get("revenue_growth"), m.get("earnings_growth")
    if rg is not None or eg is not None:
        bits = [f"revenue {_pct(rg, True)}" if rg is not None else None,
                f"earnings {_pct(eg, True)}" if eg is not None else None]
        f["growth"] = ("Strong growth: " if positive else "Weak growth: ") + ", ".join(b for b in bits if b) + " a year."
    pm, roe = m.get("profit_margin"), m.get("roe")
    if pm is not None or roe is not None:
        bits = [f"margin {_pct(pm)}" if pm is not None else None, f"ROE {_pct(roe)}" if roe is not None else None]
        f["profitability"] = ("Highly profitable: " if positive else "Thin profits: ") + ", ".join(b for b in bits if b) + "."
    de = m.get("debt_to_equity")
    fcf = m.get("free_cash_flow")
    if de is not None or fcf is not None:
        bits = [f"debt/equity {de:.2f}" if de is not None else None,
                ("positive free cash flow" if fcf and fcf > 0 else "negative free cash flow") if fcf is not None else None]
        f["health"] = ("Solid balance sheet: " if positive else "Balance-sheet strain: ") + ", ".join(b for b in bits if b) + "."
    trend, _ = _trend(m)
    f["momentum"] = ("Momentum is positive: price trend and relative strength are supportive." if positive
                     else "Momentum is negative: the price trend is working against it.")
    if trend == "down" and not positive:
        f["momentum"] = "Momentum is negative: in a downtrend below both its 50-day and 200-day averages."
    rec, tgt, price = m.get("recommendation_mean"), m.get("target_price"), m.get("price")
    if rec is not None:
        up = f", average target {_px(tgt)} ({_pct(tgt / price - 1, True)} from here)" if tgt and price else ""
        f["analysts"] = (f"Analysts are positive: rating {rec:.2f} on a 1 (strong buy) to 5 (sell) scale{up}."
                         if positive else f"Analysts are lukewarm: rating {rec:.2f} on a 1 to 5 scale{up}.")
    s = m.get("eps_surprises") or []
    if s:
        beats = sum(1 for x in s if x > 0)
        f["earnings"] = (f"Reliable earnings: beat forecasts in {beats} of {len(s)} recent quarters." if positive
                         else f"Earnings misses: beat forecasts in only {beats} of {len(s)} recent quarters.")
    r3, r5 = m.get("return_3y"), m.get("return_5y")
    if r3 is not None or r5 is not None:
        bits = [f"{_pct(r3, True)} a year over 3 years" if r3 is not None else None,
                f"{_pct(r5, True)} over 5 years" if r5 is not None else None]
        f["track_record"] = ("Strong track record: " if positive else "Weak track record: ") + ", ".join(b for b in bits if b) + "."
    vol = m.get("volatility_1y")
    if vol is not None:
        f["risk"] = (f"Relatively calm: {_pct(vol)} yearly volatility." if positive
                     else f"Risky ride: {_pct(vol)} yearly volatility"
                     + (f" and {_pct(m['drawdown'])} below its high." if m.get("drawdown") else "."))
    er, cat = m.get("expense_ratio"), m.get("category_expense_ratio")
    if er is not None:
        vs = f" vs {_pct(cat)} for similar funds" if cat else ""
        f["cost"] = (f"Low cost: {er * 100:.2f}% a year{vs}." if positive else f"Expensive: {er * 100:.2f}% a year{vs}.")
    aum = m.get("aum")
    if aum:
        f["liquidity"] = (f"Large, liquid fund: {aum / 1e9:,.1f}B in assets." if positive
                          else f"Small or thinly traded fund: {aum / 1e6:,.0f}M in assets.")
    return f


def _cases(m, r):
    pos, neg = _factor_lines(m, True), _factor_lines(m, False)
    bull = [pos[k] for k, v in r["factors"].items() if v is not None and v >= BULL_AT and k in pos]
    bear = [neg[k] for k, v in r["factors"].items() if v is not None and v <= BEAR_AT and k in neg]
    if not bull:
        bull = ["No clear strengths in the numbers right now; a bull case would rest on news or events the score can't see."]
    if not bear:
        bear = ["No clear weak spots in the numbers; the risks are in what they don't show (news, competition, the wider economy)."]
    return bull, bear


def _watch(m):
    out = []
    price, ma50, ma200 = m.get("price"), m.get("ma50"), m.get("ma200")
    if price and ma50:
        if price < ma50:
            out.append({"what": f"50-day average ({_px(ma50)})",
                        "why": "A move back above it would be the first sign the decline is easing."})
        else:
            out.append({"what": f"50-day average ({_px(ma50)})",
                        "why": "Staying above it keeps the short-term trend intact; a close below weakens it."})
    if price and ma200:
        side = "above" if price >= ma200 else "below"
        out.append({"what": f"200-day average ({_px(ma200)})",
                    "why": f"The long-term trend line. The price is {side} it now; a cross changes the long-term picture."})
    low, high = m.get("low_52w"), m.get("high_52w")
    if price and low and price <= low * 1.10:
        out.append({"what": f"52-week low ({_px(low)})",
                    "why": "Close by. A close below it would break the floor buyers have defended this year."})
    if price and high and price >= high * 0.95:
        out.append({"what": f"52-week high ({_px(high)})",
                    "why": "A close above it would be a breakout to new highs; a rejection here often means a pause."})
    if m.get("next_earnings"):
        out.append({"what": f"Earnings on {m['next_earnings']}",
                    "why": "Results and guidance can move the price sharply in either direction."})
    rsi = m.get("rsi")
    if rsi is not None and (rsi < 35 or rsi > 65):
        out.append({"what": f"RSI {rsi:.0f}", "why": "Watch for it to move back toward 50 as the stretch unwinds."})
    if m.get("target_price"):
        out.append({"what": f"Analyst target ({_px(m['target_price'])})",
                    "why": "Upgrades or downgrades around this level shift sentiment."})
    if m.get("asset_class") == "commodity":
        out.append({"what": "Interest rates and the US dollar",
                    "why": "Commodities like gold usually fall when real rates and the dollar rise, and vice versa."})
    return out


def _cautions(m, r):
    out = list(r["flags"])
    if r["confidence"] != "high":
        out.append(f"Confidence is {r['confidence']}: only {r['coverage']:.0%} of the scoring data was available.")
    out.append("The score is a screen built from numbers. It doesn't read news, so a big story can change the picture fast.")
    out.append("Prices come from Yahoo Finance and can be delayed by up to 15 minutes, or be last night's close.")
    return out


NAMES = {"track_record": "track record"}


def _gaps(m, r):
    out = [f"No data for the {NAMES.get(k, k)} factor, so it was left out of the score."
           for k, v in r["factors"].items() if v is None]
    out += list(m.get("notes") or [])
    out.append("News and events aren't part of the score; read the headlines and a full report.")
    if m.get("asset_type") == "etf":
        out.append("Doesn't look inside the fund: its holdings, tracking error or cheaper alternatives.")
    else:
        out.append("Doesn't compare valuation with competitors or read company filings and guidance.")
    if str(m.get("ticker", "")).endswith((".NS", ".BO", ".L")):
        out.append("Yahoo's data for non-US listings is often incomplete; check the exchange or company site.")
    return out


def _practices(m, r):
    out = []
    trend, _ = _trend(m)
    flags = " ".join(r["flags"]).lower()
    if trend == "down":
        out.append("Don't try to catch a falling knife: many traders wait for a higher low or a move back "
                   "above the 50-day average before buying.")
    if "overbought" in flags or (m.get("drawdown") is not None and m["drawdown"] >= -0.03):
        out.append("Avoid chasing after a big run. Waiting for a pullback, or buying in stages, lowers the risk "
                   "of buying the top.")
    if m.get("days_to_earnings") is not None and 0 <= m["days_to_earnings"] <= 21:
        out.append("Holding through earnings is a bet on one announcement. Learners often use a smaller "
                   "position or wait until after the results.")
    if "leveraged or inverse" in flags:
        out.append("Leveraged and inverse funds reset daily and lose value over time. They are tools for "
                   "short holds, not long-term investing.")
    vol = m.get("volatility_1y")
    if vol is not None and vol > 0.40:
        out.append(f"It swings a lot ({_pct(vol)} a year). A smaller position keeps normal swings from hurting.")
    if r["confidence"] == "low":
        out.append("Data is thin here, so don't act on the score alone.")
    out += [
        "Decide your exit before you enter: the price that proves you wrong (a stop) and where you'd take profit.",
        "Size each position so a 10% drop in it costs no more than about 1% of your whole portfolio.",
        "Practise with paper trades first, and write down why you bought. The journal does this for you.",
    ]
    return out


def build_brief(m: dict, r: dict) -> dict:
    trend, _ = _trend(m)
    trend_word = {"up": "uptrend", "down": "downtrend", "mixed": "no clear trend"}.get(trend, "trend unknown")
    bull, bear = _cases(m, r)
    return {
        "summary": f"{r['verdict']} with a score of {r['composite']:+.0f} out of 100, in a {trend_word}."
        if trend in ("up", "down") else f"{r['verdict']} with a score of {r['composite']:+.0f} out of 100, {trend_word}.",
        "why_moving": _why_moving(m, r) or ["Not enough price history to describe the move."],
        "bull": bull,
        "bear": bear,
        "watch": _watch(m),
        "cautions": _cautions(m, r),
        "gaps": _gaps(m, r),
        "practices": _practices(m, r),
    }
