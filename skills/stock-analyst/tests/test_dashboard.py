import importlib
import math
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture
def dash(tmp_path, monkeypatch):
    monkeypatch.setenv("STOCK_ANALYST_DATA", str(tmp_path))
    import common
    import dashboard
    import journal

    for m in (common, journal, dashboard):
        importlib.reload(m)
    return dashboard


def test_parse_tickers_cleans_and_dedupes(dash):
    ok, bad = dash.parse_tickers("aapl, gld  RELIANCE.NS;AAPL btc-usd ^nsei bad$$ " + "X" * 30)
    assert ok == ["AAPL", "GLD", "RELIANCE.NS", "BTC-USD", "^NSEI"]
    assert bad == ["BAD$$", "X" * 30]


def test_parse_tickers_caps_count(dash):
    ok, _ = dash.parse_tickers(" ".join(f"T{i}" for i in range(40)))
    assert len(ok) == dash.MAX_TICKERS


def test_clean_json_replaces_nan_and_inf(dash):
    out = dash.clean_json({"a": float("nan"), "b": [1.0, float("inf")], "c": {"d": 2}})
    assert out == {"a": None, "b": [1.0, None], "c": {"d": 2}}


@pytest.mark.parametrize("host,origin,ok", [
    ("127.0.0.1:8765", None, True),
    ("localhost:8765", "http://localhost:8765", True),
    ("127.0.0.1:8765", "http://127.0.0.1:8765", True),
    ("evil.example:8765", None, False),               # DNS rebinding
    ("127.0.0.1:8765", "https://evil.example", False),  # cross-site request
    (None, None, False),
])
def test_request_guard(dash, host, origin, ok):
    assert dash.allowed_request(host, origin) is ok


def test_journal_rows_marks_young_calls_too_early(dash):
    entries = [
        {"id": "a", "date": "2026-09-01", "ticker": "AAPL", "price": 100.0, "verdict": "BUY-lean",
         "score": 40, "benchmark": "SPY", "thesis": "x"},
        {"id": "b", "date": "2026-10-20", "ticker": "GLD", "price": 400.0, "verdict": "HOLD",
         "score": 2, "benchmark": None, "thesis": "y"},
    ]
    prices = {"AAPL": 110.0, "GLD": 380.0}
    bench = {"a": 0.05}
    rows = dash.journal_rows(entries, prices, bench, today=date(2026, 10, 23), min_age=30)
    a, b = rows  # newest first is the UI's job; order preserved here
    assert math.isclose(a["return"], 0.10)
    assert a["outcome"] == "right"
    assert b["outcome"] == "too early"
    assert math.isclose(b["return"], -0.05)


def test_journal_rows_missing_price(dash):
    rows = dash.journal_rows([{"id": "a", "date": "2026-09-01", "ticker": "ZZZ", "price": 1.0,
                               "verdict": "HOLD", "benchmark": None}], {}, {}, date(2026, 10, 23), 30)
    assert rows[0]["return"] is None and rows[0]["outcome"] == "no price"


def test_watchlist_roundtrip(dash):
    assert dash.load_watchlist() == []
    dash.save_watchlist(["aapl", "GLD", "AAPL", "bad$$"])
    assert dash.load_watchlist() == ["AAPL", "GLD"]
