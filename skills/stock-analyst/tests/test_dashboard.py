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


RSS = """<?xml version="1.0"?><rss><channel>
<item><title>Gold slides as oil jumps - Reuters</title><link>https://news.google.com/a</link>
<pubDate>Thu, 22 Oct 2026 10:00:00 GMT</pubDate><source url="https://reuters.com">Reuters</source></item>
<item><title>Newer story - CNBC</title><link>https://news.google.com/b</link>
<pubDate>Fri, 23 Oct 2026 09:00:00 GMT</pubDate><source url="https://cnbc.com">CNBC</source></item>
<item><title>Bad link</title><link>javascript:alert(1)</link><pubDate>Fri, 23 Oct 2026 08:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_parse_rss_sorts_cleans_and_drops_unsafe_links(dash):
    items = dash.parse_rss(RSS)
    assert [i["title"] for i in items] == ["Newer story", "Gold slides as oil jumps"]
    assert items[0]["source"] == "CNBC" and items[0]["date"] == "2026-10-23"
    assert all(i["url"].startswith("https://") for i in items)


def test_news_query(dash):
    assert dash.news_query("Apple Inc.", "AAPL", "stock") == "Apple AAPL stock"
    assert dash.news_query("RELIANCE INDUSTRIES LTD", "RELIANCE.NS", "stock") == "RELIANCE INDUSTRIES RELIANCE stock"
    assert dash.news_query("SPDR Gold Shares", "GLD", "etf") == "SPDR Gold Shares GLD etf"


def test_latest_report_picks_newest_for_that_ticker(dash, tmp_path):
    reports = tmp_path / "reports"
    reports.mkdir()
    (reports / "GLD-2026-09-01.md").write_text("old")
    (reports / "GLD-2026-10-23.md").write_text("# new")
    (reports / "GLDM-2026-12-01.md").write_text("other ticker")
    r = dash.latest_report("GLD")
    assert r == {"date": "2026-10-23", "markdown": "# new"}
    assert dash.latest_report("AAPL") is None
