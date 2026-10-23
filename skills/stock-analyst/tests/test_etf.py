import json
import sys
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from common import benchmark_for  # noqa: E402
from scoring import classify_asset, compute, cost, is_fund  # noqa: E402

CFG = json.loads((ROOT / "config.json").read_text())

# Close to real GLD numbers on 2026-10-23.
GLD_LIKE = {
    "ticker": "GLD", "asset_type": "etf", "asset_class": "commodity",
    "price": 366.61, "ma50": 394.51, "ma200": 414.21, "rsi": 34, "high_52w": 495.9,
    "return_6m": -0.147, "bench_return_6m": None,
    "expense_ratio": 0.004, "category_expense_ratio": 0.0082,
    "aum": 1.417e11, "premium": -0.012,
    "return_3y": 0.273, "return_5y": 0.178,
    "volatility_1y": 0.24, "drawdown": -0.261,
}

CHEAP_INDEX_UPTREND = {
    "ticker": "VOO", "asset_type": "etf", "asset_class": "equity",
    "price": 110, "ma50": 105, "ma200": 95, "rsi": 60, "high_52w": 112,
    "return_6m": 0.12, "bench_return_6m": 0.07,
    "expense_ratio": 0.0003, "category_expense_ratio": 0.007,
    "aum": 5e11, "premium": 0.0002,
    "return_3y": 0.15, "return_5y": 0.13,
    "volatility_1y": 0.14, "drawdown": -0.02,
}


def test_is_fund_detects_us_and_indian_etfs():
    assert is_fund("ETF", "SPDR Gold Shares")
    assert is_fund("MUTUALFUND", "Vanguard 500")
    assert is_fund("EQUITY", "NIP IND ETF GOLD BEES")  # Yahoo labels Indian ETFs as equity
    assert not is_fund("EQUITY", "Apple Inc.")
    assert not is_fund("EQUITY", None)


@pytest.mark.parametrize("category,name,expected", [
    ("Commodities Focused", "SPDR Gold Shares", "commodity"),
    (None, "NIP IND ETF GOLD BEES", "commodity"),
    ("Long Government", "iShares 20+ Year Treasury Bond", "bond"),
    ("Intermediate Core Bond", "iShares Core US Aggregate", "bond"),
    ("Digital Assets", "iShares Bitcoin Trust", "crypto"),
    ("Large Blend", "SPDR S&P 500", "equity"),
    (None, "NIP IND ETF NIFTY BEES", "equity"),
])
def test_classify_asset(category, name, expected):
    assert classify_asset(category, name) == expected


def test_benchmark_depends_on_asset_class():
    assert benchmark_for("VOO", "equity") == "SPY"
    assert benchmark_for("NIFTYBEES.NS", "equity") == "^NSEI"
    assert benchmark_for("TLT", "bond") == "AGG"
    assert benchmark_for("GLD", "commodity") is None  # judged on absolute return
    assert benchmark_for("GOLDBEES.NS", "commodity") is None
    assert benchmark_for("SPY", "equity") is None  # never compare a fund with itself
    assert benchmark_for("AAPL") == "SPY"  # stocks unchanged


def test_cost_rewards_cheap_funds():
    assert cost({"expense_ratio": 0.0003}) == 1.0
    assert cost({"expense_ratio": 0.0100}) == -1.0
    assert cost({}) is None


def test_cheap_index_fund_in_uptrend_is_buy_lean():
    r = compute(CHEAP_INDEX_UPTREND, CFG)
    assert set(r["factors"]) == set(CFG["etf_weights"])
    assert r["verdict"] == "BUY-lean"
    assert r["confidence"] == "high"


def test_gold_in_downtrend_is_hold_not_sell():
    # Momentum is bad, but a cheap, huge fund with a strong record is not a SELL on that alone.
    r = compute(GLD_LIKE, CFG)
    assert r["verdict"] == "HOLD"
    assert r["factors"]["momentum"] < 0
    assert any("below its 52-week high" in f for f in r["flags"])


def test_etf_flags():
    risky = {**GLD_LIKE, "name": "ProShares UltraPro QQQ 3x", "expense_ratio": 0.0095,
             "aum": 4e7, "premium": 0.03}
    flags = " | ".join(compute(risky, CFG)["flags"])
    assert "Leveraged or inverse" in flags
    assert "expense ratio" in flags
    assert "Small fund" in flags
    assert "premium" in flags
    assert "analysts" not in flags  # analyst coverage is a stock concept


def test_indian_etf_without_fund_data_still_scores():
    thin = {k: GLD_LIKE[k] for k in ("asset_type", "asset_class", "price", "ma50", "ma200",
                                      "rsi", "high_52w", "return_6m", "volatility_1y", "drawdown")}
    r = compute(thin, CFG)
    assert r["factors"]["cost"] is None
    assert r["factors"]["momentum"] is not None
    assert r["confidence"] == "low"


def test_journal_accepts_absolute_benchmark(tmp_path, monkeypatch):
    import importlib

    monkeypatch.setenv("STOCK_ANALYST_DATA", str(tmp_path))
    import common
    import journal
    importlib.reload(common)
    importlib.reload(journal)
    journal.cmd_add(Namespace(ticker="GLD", price=366.61, verdict="HOLD", score=2.0, target=None,
                              source="quick", thesis="t", benchmark="none"))
    journal.cmd_add(Namespace(ticker="VOO", price=500.0, verdict="BUY-lean", score=40.0, target=None,
                              source="quick", thesis="t", benchmark=None))
    gld, voo = journal.load()
    assert gld["benchmark"] is None
    assert voo["benchmark"] == "SPY"
