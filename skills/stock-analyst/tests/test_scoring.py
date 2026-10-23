import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from scoring import _scale, compute, valuation  # noqa: E402

CFG = json.loads((ROOT / "config.json").read_text())

STRONG = {
    "price": 110, "ma50": 105, "ma200": 95, "rsi": 60, "high_52w": 130,
    "return_6m": 0.25, "bench_return_6m": 0.05,
    "trailing_pe": 18, "forward_pe": 15, "peg": 1.0,
    "revenue_growth": 0.25, "earnings_growth": 0.30,
    "profit_margin": 0.25, "roe": 0.30,
    "debt_to_equity": 0.3, "current_ratio": 2.0, "free_cash_flow": 1e9,
    "recommendation_mean": 1.5, "target_price": 140, "analyst_count": 20,
    "eps_surprises": [0.08, 0.05, 0.10, 0.06],
}

WEAK = {
    "price": 80, "ma50": 85, "ma200": 100, "rsi": 45, "high_52w": 130,
    "return_6m": -0.30, "bench_return_6m": 0.05,
    "trailing_pe": -5, "forward_pe": None, "peg": None,
    "revenue_growth": -0.10, "earnings_growth": -0.40,
    "profit_margin": -0.05, "roe": -0.10,
    "debt_to_equity": 3.0, "current_ratio": 0.6, "free_cash_flow": -1e8,
    "recommendation_mean": 4.0, "target_price": 70, "analyst_count": 10,
    "eps_surprises": [-0.10, -0.05, -0.12, 0.01],
}


def test_scale_maps_endpoints_and_clamps():
    assert _scale(0.25, -0.05, 0.25) == 1.0
    assert _scale(-0.05, -0.05, 0.25) == -1.0
    assert _scale(10, 0, 1) == 1.0
    assert _scale(45, 45, 12) == -1.0  # works when "bad" is above "good"
    assert _scale(None, 0, 1) is None


def test_strong_company_is_buy_lean():
    r = compute(STRONG, CFG)
    assert r["verdict"] == "BUY-lean"
    assert r["composite"] > 60
    assert r["confidence"] == "high"


def test_weak_company_is_sell_lean_with_flags():
    r = compute(WEAK, CFG)
    assert r["verdict"] == "SELL-lean"
    assert any("leverage" in f for f in r["flags"])
    assert any("Loss-making" in f for f in r["flags"])


def test_negative_pe_scores_worst_valuation():
    assert valuation({"trailing_pe": -3}) == -1.0


def test_missing_factors_reduce_coverage_not_score():
    sparse = {"price": 110, "ma50": 105, "ma200": 95, "rsi": 60}
    r = compute(sparse, CFG)
    assert r["factors"]["valuation"] is None
    assert r["confidence"] == "low"
    assert r["composite"] > 0  # momentum alone still counts


def test_earnings_soon_downgrades_buy():
    r = compute({**STRONG, "days_to_earnings": 5}, CFG)
    assert r["verdict"] == "HOLD (wait for earnings)"


def test_few_analysts_ignored():
    r = compute({**STRONG, "analyst_count": 1}, CFG)
    assert r["factors"]["analysts"] is None


def test_no_data_at_all():
    r = compute({}, CFG)
    assert r["composite"] == 0.0 and r["coverage"] == 0.0


def test_thin_data_is_labelled_and_crypto_skips_analyst_flag():
    r = compute({"ticker": "BTC-USD", "price": 110, "ma50": 105, "ma200": 95, "rsi": 60}, CFG)
    assert r["verdict"].endswith("(thin data)")
    assert not any("analysts" in f for f in r["flags"])
