"""Pure scoring logic: turns a metrics dict into factor scores and a verdict.

No third-party imports, so it can be unit-tested offline.
Every factor returns a value in [-1, 1], or None when its data is missing.
Missing factors are dropped and the remaining weights are renormalised.
"""

from __future__ import annotations

import math
import re


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _avg(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def _scale(x, bad, good):
    """Map x linearly so `bad` -> -1 and `good` -> +1 (bad may be above good)."""
    if x is None:
        return None
    return _clamp(-1 + 2 * (x - bad) / (good - bad))


def valuation(m: dict):
    pe = m.get("forward_pe") or m.get("trailing_pe")
    pe_s = None
    if pe is not None:
        pe_s = -1.0 if pe <= 0 else _scale(pe, 45, 12)  # negative P/E = losses
    peg = m.get("peg")
    peg_s = _scale(peg, 3.0, 1.0) if peg is not None and peg > 0 else None
    return _avg([pe_s, peg_s])


def growth(m: dict):
    return _avg([
        _scale(m.get("revenue_growth"), -0.05, 0.25),
        _scale(m.get("earnings_growth"), -0.10, 0.30),
    ])


def profitability(m: dict):
    return _avg([
        _scale(m.get("profit_margin"), 0.0, 0.25),
        _scale(m.get("roe"), 0.0, 0.25),
    ])


def health(m: dict):
    fcf = m.get("free_cash_flow")
    return _avg([
        _scale(m.get("debt_to_equity"), 2.0, 0.3),
        _scale(m.get("current_ratio"), 0.8, 2.0),
        None if fcf is None else (0.5 if fcf > 0 else -0.5),
    ])


def momentum(m: dict):
    price, ma50, ma200, rsi = (m.get(k) for k in ("price", "ma50", "ma200", "rsi"))
    vs_200 = _scale(price / ma200 - 1, -0.15, 0.15) if price and ma200 else None
    cross = (0.5 if ma50 > ma200 else -0.5) if ma50 and ma200 else None
    rsi_s = None
    if rsi is not None:
        rsi_s = -0.5 if rsi > 75 else (0.3 if rsi < 25 else 0.0)
    rel = m.get("return_6m")
    bench = m.get("bench_return_6m")
    rel_s = _scale(rel - bench, -0.2, 0.2) if rel is not None and bench is not None else None
    return _avg([vs_200, cross, rsi_s, rel_s])


def analysts(m: dict):
    if (m.get("analyst_count") or 0) < 3:
        return None  # too few analysts to mean anything
    price, target = m.get("price"), m.get("target_price")
    upside = target / price - 1 if price and target else None
    return _avg([
        _scale(m.get("recommendation_mean"), 4.0, 1.5),  # 1 = strong buy, 5 = sell
        _scale(upside, -0.10, 0.30),
    ])


def earnings(m: dict):
    surprises = m.get("eps_surprises") or []
    if not surprises:
        return None
    beat_rate = sum(1 for s in surprises if s > 0) / len(surprises)
    return _avg([
        _scale(sum(surprises) / len(surprises), -0.10, 0.10),
        _scale(beat_rate, 0.0, 1.0),
    ])


FACTORS = {
    "valuation": valuation,
    "growth": growth,
    "profitability": profitability,
    "health": health,
    "momentum": momentum,
    "analysts": analysts,
    "earnings": earnings,
}


# ---------- Funds (ETFs) ----------
# Company factors (P/E, margins, analysts, earnings) don't exist for a fund,
# so ETFs get their own factor set, weighted by config.json "etf_weights".

_CRYPTO = re.compile(r"digital asset|bitcoin|\bether(eum)?\b|crypto", re.I)
_COMMODITY = re.compile(r"commodit|precious|\bgold\b|\bsilver\b|\boil\b|natural gas|\bmetals?\b", re.I)
_BOND = re.compile(r"bond|treasur|government|fixed income|\bmuni|credit|inflation-protected|t-bill", re.I)
_LEVERAGED = re.compile(r"\b(ultra|ultrapro|inverse|bear)\b|\b-?\d(\.\d)?x\b", re.I)


def is_fund(quote_type: str | None, name: str | None) -> bool:
    """True for ETFs and mutual funds. Yahoo labels Indian ETFs as EQUITY, so check the name too."""
    if quote_type in ("ETF", "MUTUALFUND"):
        return True
    return bool(re.search(r"\bETF\b|BEES\b", name or "", re.I))


def classify_asset(category: str | None, name: str | None) -> str:
    """Rough asset class of a fund: crypto, commodity, bond or equity."""
    text = f"{category or ''} {name or ''}"
    for label, pattern in (("crypto", _CRYPTO), ("commodity", _COMMODITY), ("bond", _BOND)):
        if pattern.search(text):
            return label
    return "equity"


def track_record(m: dict):
    return _avg([
        _scale(m.get("return_3y"), 0.0, 0.15),
        _scale(m.get("return_5y"), 0.0, 0.12),
    ])


def risk(m: dict):
    return _avg([
        _scale(m.get("volatility_1y"), 0.40, 0.10),
        _scale(m.get("drawdown"), -0.30, 0.0),  # distance below the 52-week high
    ])


def cost(m: dict):
    er, cat = m.get("expense_ratio"), m.get("category_expense_ratio")
    return _avg([
        _scale(er, 0.0075, 0.0005),
        _scale(er / cat, 1.5, 0.3) if er is not None and cat else None,
    ])


def liquidity(m: dict):
    aum, prem = m.get("aum"), m.get("premium")
    return _avg([
        _scale(math.log10(aum), 8.0, 10.0) if aum else None,  # $100M -> -1, $10B -> +1
        _scale(abs(prem), 0.02, 0.002) if prem is not None else None,
    ])


ETF_FACTORS = {
    "momentum": momentum,
    "track_record": track_record,
    "risk": risk,
    "cost": cost,
    "liquidity": liquidity,
}


def etf_flags(m: dict, cfg: dict) -> list[str]:
    out = []
    if _LEVERAGED.search(m.get("name") or ""):
        out.append("Leveraged or inverse fund: built for days, not months; returns decay over time")
    dd = m.get("drawdown")
    if dd is not None and dd <= -0.20:
        out.append(f"Bear market: {abs(dd):.0%} below its 52-week high")
    rsi, price, high = m.get("rsi"), m.get("price"), m.get("high_52w")
    if rsi is not None and rsi > 70 and price and high and price >= 0.95 * high:
        out.append(f"Overbought: RSI {rsi:.0f} and within 5% of 52-week high")
    er = m.get("expense_ratio")
    if er is not None and er > 0.0075:
        out.append(f"High expense ratio: {er:.2%} a year")
    aum = m.get("aum")
    if aum is not None and aum < 1e8:
        out.append(f"Small fund ({aum / 1e6:.0f}M in assets): higher closure risk and wider spreads")
    prem = m.get("premium")
    if prem is not None and abs(prem) > 0.02:
        side = "premium" if prem > 0 else "discount"
        out.append(f"Trading at a {abs(prem):.1%} {side} to the value of its holdings (NAV)")
    return out


def flags(m: dict, cfg: dict) -> list[str]:
    out = []
    days = m.get("days_to_earnings")
    if days is not None and 0 <= days <= cfg.get("earnings_warning_days", 14):
        out.append(f"Earnings in {days} days: expect a big move either way")
    rsi, price, high = m.get("rsi"), m.get("price"), m.get("high_52w")
    if rsi is not None and rsi > 70 and price and high and price >= 0.95 * high:
        out.append(f"Overbought: RSI {rsi:.0f} and within 5% of 52-week high")
    de = m.get("debt_to_equity")
    if de is not None and de > 2:
        out.append(f"High leverage: debt/equity {de:.1f}x")
    pe = m.get("trailing_pe")
    if pe is not None and pe <= 0:
        out.append("Loss-making on a trailing basis")
    is_crypto = str(m.get("ticker", "")).upper().endswith("-USD")
    if not is_crypto and (m.get("analyst_count") or 0) < 3:
        out.append("Fewer than 3 analysts cover this stock")
    return out


def compute(m: dict, cfg: dict) -> dict:
    """Score a metrics dict. `cfg` holds `weights`, `etf_weights` and `thresholds` (see config.json)."""
    is_etf = m.get("asset_type") == "etf"
    weights = cfg["etf_weights"] if is_etf else cfg["weights"]
    table = ETF_FACTORS if is_etf else FACTORS
    factors = {name: table[name](m) for name in weights}
    used = {k: w for k, w in weights.items() if factors[k] is not None}
    total_w = sum(weights.values())
    coverage = sum(used.values()) / total_w if total_w else 0.0
    if used:
        composite = 100 * sum(factors[k] * w for k, w in used.items()) / sum(used.values())
    else:
        composite = 0.0

    th = cfg["thresholds"]
    if composite >= th["buy"]:
        verdict = "BUY-lean"
    elif composite <= th["sell"]:
        verdict = "SELL-lean"
    else:
        verdict = "HOLD"
    found = etf_flags(m, th) if is_etf else flags(m, th)
    if verdict == "BUY-lean" and any(f.startswith("Earnings in") for f in found):
        verdict = "HOLD (wait for earnings)"

    if coverage < 0.4:
        verdict += " (thin data)"  # e.g. crypto: momentum is the only factor

    confidence = "high" if coverage >= 0.85 else "medium" if coverage >= 0.6 else "low"
    return {
        "factors": factors,
        "composite": round(composite, 1),
        "verdict": verdict,
        "coverage": round(coverage, 2),
        "confidence": confidence,
        "flags": found,
    }
