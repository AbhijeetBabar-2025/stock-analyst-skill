import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from brief import build_brief  # noqa: E402
from scoring import compute  # noqa: E402

CFG = json.loads((ROOT / "config.json").read_text())

GLD = {
    "ticker": "GLD", "name": "SPDR Gold Shares", "currency": "USD",
    "asset_type": "etf", "asset_class": "commodity", "benchmark": None,
    "price": 366.61, "ma50": 394.51, "ma200": 414.21, "rsi": 34, "high_52w": 495.9, "low_52w": 362.32,
    "return_1m": -0.064, "return_3m": -0.021, "return_6m": -0.147, "drawdown": -0.261,
    "expense_ratio": 0.004, "category_expense_ratio": 0.0082, "aum": 1.417e11, "premium": -0.012,
    "return_3y": 0.273, "return_5y": 0.178, "volatility_1y": 0.286, "notes": [],
}

AAPL = {
    "ticker": "AAPL", "name": "Apple Inc.", "currency": "USD", "asset_type": "stock", "benchmark": "SPY",
    "price": 347.7, "ma50": 329.5, "ma200": 294.1, "rsi": 64, "high_52w": 348.2, "low_52w": 246.0,
    "return_1m": 0.05, "return_3m": 0.12, "return_6m": 0.30, "bench_return_6m": 0.068, "drawdown": -0.001,
    "volatility_1y": 0.25, "trailing_pe": 39.9, "forward_pe": 36.3, "peg": 2.71,
    "revenue_growth": 0.164, "earnings_growth": 0.287, "profit_margin": 0.276, "roe": 1.488,
    "debt_to_equity": 0.78, "current_ratio": 0.9, "free_cash_flow": 1e11,
    "recommendation_mean": 2.25, "target_price": 328.35, "analyst_count": 39,
    "eps_surprises": [0.05, 0.04, 0.06, 0.03], "days_to_earnings": 10, "next_earnings": "2026-11-02",
    "notes": ["Earnings calendar unavailable (HTTPError)"],
}


def brief(m):
    return build_brief(m, compute(m, CFG))


def text(items):
    return " | ".join(i if isinstance(i, str) else f"{i['what']} {i['why']}" for i in items)


def test_brief_has_every_section():
    b = brief(GLD)
    for key in ("summary", "why_moving", "bull", "bear", "watch", "cautions", "gaps", "practices"):
        assert key in b and b[key], key


def test_downtrend_explained_with_numbers():
    why = text(brief(GLD)["why_moving"])
    assert "downtrend" in why.lower()
    assert "26.1%" in why  # distance below the 52-week high
    assert "6.4%" in why  # one-month fall


def test_bull_and_bear_come_from_factors():
    b = brief(GLD)
    assert "track record" in text(b["bull"]).lower()
    assert "momentum" in text(b["bear"]).lower() or "trend" in text(b["bear"]).lower()
    a = brief(AAPL)
    assert "growth" in text(a["bull"]).lower()
    assert "valuation" in text(a["bear"]).lower() or "p/e" in text(a["bear"]).lower()


def test_watch_levels_use_real_prices():
    w = text(brief(GLD)["watch"])
    assert "394.51" in w  # 50-day average to reclaim
    assert "362.32" in w  # 52-week low close by
    assert "2026-11-02" in text(brief(AAPL)["watch"])


def test_practices_are_tailored_and_labelled_for_learning():
    g = text(brief(GLD)["practices"]).lower()
    assert "falling knife" in g
    a = text(brief(AAPL)["practices"]).lower()
    assert "earnings" in a
    assert "exit" in a  # baseline practice always present


def test_leveraged_fund_practice():
    lev = {**GLD, "name": "ProShares UltraPro QQQ 3x", "asset_class": "equity"}
    assert "daily" in text(brief(lev)["practices"]).lower()


def test_gaps_list_missing_data_and_notes():
    thin = {k: GLD[k] for k in ("ticker", "name", "asset_type", "asset_class", "benchmark", "price",
                                "ma50", "ma200", "rsi", "high_52w", "low_52w", "return_6m",
                                "drawdown", "volatility_1y")}
    thin["notes"] = ["No fund data on Yahoo"]
    g = text(brief(thin)["gaps"])
    assert "cost" in g.lower() and "No fund data on Yahoo" in g
    assert "Earnings calendar unavailable" in text(brief(AAPL)["gaps"])


def test_no_em_dashes_in_generated_text():
    for m in (GLD, AAPL):
        assert "—" not in json.dumps(brief(m), ensure_ascii=False)
