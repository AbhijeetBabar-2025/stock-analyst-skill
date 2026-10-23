#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["yfinance>=0.2.40", "pandas>=2.0"]
# ///
"""Local web dashboard: scan tickers and browse the journal in the browser.

Usage:
    uv run dashboard.py            # http://127.0.0.1:8787
    uv run dashboard.py --port 9000 --open

Listens on 127.0.0.1 only. Uses the same scoring as score.py and the same
journal and watchlist files in ~/.stock-analyst/.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import xml.etree.ElementTree as ET
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from email.utils import parsedate_to_datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import journal
from brief import build_brief
from common import DATA_DIR, SKILL_DIR, load_config

WEB_DIR = SKILL_DIR / "web"
STATIC = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
          "/app.css": ("app.css", "text/css")}
WATCHLIST = DATA_DIR / "watchlist.json"
REPORTS = DATA_DIR / "reports"
NEWS_SECONDS = 900
_NAME_NOISE = re.compile(r"\b(inc|corp|corporation|co|ltd|limited|plc|holdings?|company)\b\.?", re.I)
MAX_TICKERS = 20
CACHE_SECONDS = 300
LOCAL_HOSTS = {"127.0.0.1", "localhost", "[::1]", "::1"}
_TICKER = re.compile(r"^\^?[A-Z0-9][A-Z0-9.\-=]{0,14}$")

_cache: dict[str, tuple[float, dict]] = {}
_news_cache: dict[str, tuple[float, list]] = {}
_cache_lock = threading.Lock()


# ---------- Pure helpers (unit-tested) ----------

def parse_tickers(text: str) -> tuple[list[str], list[str]]:
    """Split user input into valid Yahoo symbols (deduped, max MAX_TICKERS) and rejects."""
    ok, bad = [], []
    for raw in re.split(r"[\s,;]+", text or ""):
        t = raw.strip().upper()
        if not t:
            continue
        if _TICKER.match(t):
            if t not in ok and len(ok) < MAX_TICKERS:
                ok.append(t)
        else:
            bad.append(t)
    return ok, bad


def clean_json(obj):
    """NaN and infinity are not valid JSON; turn them into null."""
    if isinstance(obj, float):
        return None if math.isnan(obj) or math.isinf(obj) else obj
    if isinstance(obj, dict):
        return {k: clean_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [clean_json(v) for v in obj]
    return obj


def _hostname(value: str) -> str:
    v = value.strip().lower()
    if v.startswith("["):
        return v[: v.index("]") + 1] if "]" in v else v
    return v.rsplit(":", 1)[0] if v.count(":") == 1 else v


def allowed_request(host: str | None, origin: str | None) -> bool:
    """Only answer requests addressed to this machine, from pages served by this machine.

    The Host check blocks DNS-rebinding; the Origin check blocks other websites
    from posting to the local server.
    """
    if not host or _hostname(host) not in LOCAL_HOSTS:
        return False
    if origin is None:
        return True
    parsed = urlparse(origin)
    return parsed.scheme == "http" and (parsed.hostname or "") in {h.strip("[]") for h in LOCAL_HOSTS}


def journal_rows(entries: list[dict], prices: dict[str, float], bench: dict[str, float],
                 today: date, min_age: int) -> list[dict]:
    """Attach current price, return since the call and outcome to each journal entry."""
    rows = []
    for e in entries:
        age = (today - date.fromisoformat(e["date"])).days
        price = prices.get(e["ticker"])
        ret = price / e["price"] - 1 if price else None
        b = bench.get(e["id"])
        if ret is None:
            outcome = "no price"
        elif age < min_age:
            outcome = "too early"
        else:
            outcome = journal.judge(e["verdict"], ret, b)
        rows.append({**e, "current": price, "return": ret, "bench_return": b,
                     "age_days": age, "outcome": outcome})
    return rows


def parse_rss(xml_text: str, limit: int = 6) -> list[dict]:
    """Headlines from a Google News RSS feed, newest first. Only http(s) links survive."""
    items = []
    for it in ET.fromstring(xml_text).iter("item"):
        url = (it.findtext("link") or "").strip()
        if not url.startswith(("https://", "http://")):
            continue
        source = (it.findtext("source") or "").strip()
        title = (it.findtext("title") or "").strip()
        if source and title.endswith(f" - {source}"):
            title = title[: -len(source) - 3]
        try:
            when = parsedate_to_datetime(it.findtext("pubDate") or "")
        except (TypeError, ValueError):
            when = None
        items.append({"title": title, "source": source, "url": url,
                      "date": when.date().isoformat() if when else None, "_ts": when.timestamp() if when else 0})
    items.sort(key=lambda i: i["_ts"], reverse=True)
    return [{k: v for k, v in i.items() if k != "_ts"} for i in items[:limit]]


def news_query(name: str, ticker: str, asset_type: str) -> str:
    """Search words for a ticker: company name without suffixes, base symbol, and kind."""
    clean = re.sub(r"[^\w\s&]", " ", _NAME_NOISE.sub(" ", name or ""))
    words = " ".join(clean.split()[:4])
    base = ticker.split(".")[0].lstrip("^")
    return f"{words} {base} {'etf' if asset_type == 'etf' else 'stock'}".strip()


def latest_report(ticker: str) -> dict | None:
    """Newest saved full report for this ticker (written by Claude in Report mode)."""
    if not REPORTS.is_dir():
        return None
    files = sorted(p for p in REPORTS.glob(f"{ticker}-*.md")
                   if re.fullmatch(rf"{re.escape(ticker)}-\d{{4}}-\d{{2}}-\d{{2}}", p.stem))
    if not files:
        return None
    return {"date": files[-1].stem[len(ticker) + 1:], "markdown": files[-1].read_text()}


def load_watchlist() -> list[str]:
    if not WATCHLIST.exists():
        return []
    try:
        return parse_tickers(" ".join(json.loads(WATCHLIST.read_text())))[0]
    except (json.JSONDecodeError, TypeError):
        return []


def save_watchlist(tickers: list[str]) -> list[str]:
    clean = parse_tickers(" ".join(tickers))[0]
    WATCHLIST.parent.mkdir(parents=True, exist_ok=True)
    WATCHLIST.write_text(json.dumps(clean) + "\n")
    return clean


# ---------- Data (network) ----------

def scan_one(ticker: str, cfg: dict) -> dict:
    with _cache_lock:
        hit = _cache.get(ticker)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]
    import score  # imported lazily: pulls in yfinance

    try:
        m = score.fetch(ticker)
        out = {"ticker": ticker, "ok": True, "metrics": m, "result": score.compute(m, cfg),
               "scanned_at": time.strftime("%H:%M:%S")}
    except Exception as e:
        return {"ticker": ticker, "ok": False, "error": str(e)}
    with _cache_lock:
        _cache[ticker] = (time.time(), out)
    return out


def fetch_news(query: str) -> tuple[list[dict], str | None]:
    """Headlines from Google News (last 7 days), cached. Returns (items, error)."""
    hit = _news_cache.get(query)
    if hit and time.time() - hit[0] < NEWS_SECONDS:
        return hit[1], None
    url = ("https://news.google.com/rss/search?" +
           urllib.parse.urlencode({"q": f"{query} when:7d", "hl": "en-US", "gl": "US", "ceid": "US:en"}))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 stock-analyst-dashboard"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            items = parse_rss(resp.read(1_000_000).decode("utf-8", "replace"))
    except Exception as e:
        return [], f"Couldn't load headlines ({type(e).__name__}); try again in a minute."
    _news_cache[query] = (time.time(), items)
    return items, None


def detail(ticker: str) -> dict:
    """Everything the detail panel shows for one ticker."""
    s = scan_one(ticker, load_config())
    if not s["ok"]:
        return {"ticker": ticker, "ok": False, "error": s["error"]}
    m, r = s["metrics"], s["result"]
    news, news_error = fetch_news(news_query(m["name"], ticker, m.get("asset_type", "stock")))
    return {"ticker": ticker, "ok": True, "metrics": m, "result": r, "brief": build_brief(m, r),
            "news": news, "news_error": news_error, "report": latest_report(ticker)}


def scan(tickers: list[str]) -> list[dict]:
    cfg = load_config()
    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(lambda t: scan_one(t, cfg), tickers))


def journal_view() -> tuple[list[dict], list[str]]:
    """Journal rows (newest first) plus notes about any data that couldn't be fetched."""
    from common import import_yfinance, latest_prices

    entries = journal.load()
    if not entries:
        return [], []
    notes, prices = [], {}
    for t in sorted({e["ticker"] for e in entries}):
        try:
            prices.update(latest_prices([t]))
        except Exception as e:
            notes.append(f"No current price for {t}: {e}")
    yf = import_yfinance()
    bench = {}
    for e in entries:
        if not e.get("benchmark"):
            continue
        try:
            c = yf.Ticker(e["benchmark"]).history(start=e["date"], auto_adjust=True)["Close"].dropna()
            if not c.empty:
                bench[e["id"]] = float(c.iloc[-1] / c.iloc[0] - 1)
            else:
                notes.append(f"No {e['benchmark']} prices since {e['date']}; {e['ticker']} judged on its own return")
        except Exception as ex:
            notes.append(f"Couldn't fetch {e['benchmark']} ({ex}); {e['ticker']} judged on its own return")
    rows = journal_rows(entries, prices, bench, date.today(), load_config()["review"]["min_age_days"])
    return list(reversed(rows)), notes


# ---------- HTTP ----------

class Handler(BaseHTTPRequestHandler):
    server_version = "StockAnalyst"

    def log_message(self, fmt, *args):  # keep the terminal quiet; errors are sent to the page
        pass

    def _guard(self) -> bool:
        if allowed_request(self.headers.get("Host"), self.headers.get("Origin")):
            return True
        self._send(403, {"error": "Requests are only accepted from this computer."})
        return False

    def _send(self, status: int, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(clean_json(payload), default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict:
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            raise ValueError("Send JSON with Content-Type: application/json")
        n = int(self.headers.get("Content-Length") or 0)
        if n > 64_000:
            raise ValueError("Request too large")
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        if not self._guard():
            return
        url = urlparse(self.path)
        if url.path in STATIC:
            name, ctype = STATIC[url.path]
            return self._send(200, (WEB_DIR / name).read_bytes(), ctype)
        try:
            if url.path == "/api/scan":
                ok, bad = parse_tickers(parse_qs(url.query).get("t", [""])[0])
                if not ok:
                    return self._send(400, {"error": "Add at least one valid symbol, e.g. AAPL or RELIANCE.NS"})
                return self._send(200, {"results": scan(ok), "rejected": bad})
            if url.path == "/api/detail":
                ok, _ = parse_tickers(parse_qs(url.query).get("t", [""])[0])
                if not ok:
                    return self._send(400, {"error": "Missing or invalid symbol"})
                return self._send(200, detail(ok[0]))
            if url.path == "/api/watchlist":
                return self._send(200, {"tickers": load_watchlist()})
            if url.path == "/api/journal":
                rows, notes = journal_view()
                return self._send(200, {"rows": rows, "notes": notes,
                                        "min_age_days": load_config()["review"]["min_age_days"]})
        except Exception as e:
            return self._send(500, {"error": f"{type(e).__name__}: {e}"})
        self._send(404, {"error": "Not found"})

    def do_POST(self):
        if not self._guard():
            return
        try:
            body = self._body()
            if self.path == "/api/watchlist":
                return self._send(200, {"tickers": save_watchlist(list(body.get("tickers", [])))})
            if self.path == "/api/journal":
                ok, _ = parse_tickers(str(body.get("ticker", "")))
                price = float(body.get("price") or 0)
                verdict = str(body.get("verdict", ""))[:40]
                if not ok or price <= 0 or not verdict:
                    return self._send(400, {"error": "Need a valid ticker, price and verdict"})
                entry = journal.new_entry(Namespace(
                    ticker=ok[0], price=round(price, 4), verdict=verdict,
                    score=body.get("score"), target=None, source="quick",
                    thesis=str(body.get("thesis", ""))[:300],
                    benchmark=body.get("benchmark") or "none",
                ))
                journal.append(entry)
                return self._send(200, {"entry": entry})
        except (ValueError, json.JSONDecodeError) as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:
            return self._send(500, {"error": f"{type(e).__name__}: {e}"})
        self._send(404, {"error": "Not found"})


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8787)
    p.add_argument("--open", action="store_true", help="open the dashboard in your browser")
    a = p.parse_args()
    try:
        server = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    except OSError as e:
        print(f"Could not start on port {a.port} ({e}). Try another: --port 8788", file=sys.stderr)
        return 1
    url = f"http://127.0.0.1:{a.port}"
    print(f"Stock Analyst dashboard running at {url}  (Ctrl+C to stop)")
    if a.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
