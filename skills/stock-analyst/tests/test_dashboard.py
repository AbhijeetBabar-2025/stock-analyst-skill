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


def test_portfolio_view_totals_per_currency(dash):
    holdings = {"AAPL": {"qty": 10, "avg_cost": 200.0}, "GLD": {"qty": 5, "avg_cost": 400.0},
                "TCS.NS": {"qty": 4, "avg_cost": 3000.0}}
    quotes = {
        "AAPL": {"price": 300.0, "currency": "USD", "name": "Apple", "verdict": "HOLD", "score": 35, "asset_type": "stock"},
        "GLD": {"price": 360.0, "currency": "USD", "name": "Gold", "verdict": "HOLD", "score": 2, "asset_type": "etf"},
        "TCS.NS": {"price": 2500.0, "currency": "INR", "name": "TCS", "verdict": "SELL-lean", "score": -30, "asset_type": "stock"},
    }
    v = dash.portfolio_view(holdings, quotes, {})
    rows = {r["ticker"]: r for r in v["rows"]}
    assert rows["AAPL"]["value"] == 3000.0
    assert math.isclose(rows["AAPL"]["pnl_pct"], 0.5)
    assert math.isclose(rows["GLD"]["pnl"], -200.0)
    # weights are within each currency: USD total 4800
    assert math.isclose(rows["AAPL"]["weight"], 3000 / 4800)
    assert rows["AAPL"]["concentrated"] is True and rows["TCS.NS"]["weight"] == 1.0
    usd = v["totals"]["USD"]
    assert usd == {"value": 4800.0, "cost": 4000.0, "pnl": 800.0, "pnl_pct": 0.2, "count": 2}
    assert v["totals"]["INR"]["pnl"] == -2000.0
    assert [r["ticker"] for r in v["rows"]][:2] == ["AAPL", "GLD"]  # USD by value, then INR


def test_portfolio_view_missing_quote(dash):
    v = dash.portfolio_view({"ZZZ": {"qty": 1, "avg_cost": 5.0}}, {}, {"ZZZ": "No price history"})
    row = v["rows"][0]
    assert row["price"] is None and row["value"] is None and row["error"] == "No price history"
    assert v["totals"] == {}


@pytest.mark.parametrize("body,expected", [
    ({"action": "add", "ticker": "aapl", "qty": "10", "cost": 180}, ("add", "AAPL", 10.0, 180.0)),
    ({"action": "remove", "ticker": "GLD"}, ("remove", "GLD", None, None)),
    ({"action": "remove", "ticker": "GLD", "qty": 2}, ("remove", "GLD", 2.0, None)),
])
def test_parse_trade_ok(dash, body, expected):
    assert dash.parse_trade(body) == expected


@pytest.mark.parametrize("body", [
    {"action": "add", "ticker": "AAPL", "qty": 0, "cost": 10},
    {"action": "add", "ticker": "AAPL", "qty": 1, "cost": -5},
    {"action": "add", "ticker": "AAPL", "qty": "abc", "cost": 5},
    {"action": "add", "ticker": "bad$$", "qty": 1, "cost": 5},
    {"action": "sell-everything", "ticker": "AAPL"},
    {"action": "remove", "ticker": "AAPL", "qty": -1},
])
def test_parse_trade_rejects_bad_input(dash, body):
    with pytest.raises(ValueError):
        dash.parse_trade(body)
