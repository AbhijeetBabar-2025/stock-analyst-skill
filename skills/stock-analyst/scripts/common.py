"""Shared paths and helpers for the stock-analyst scripts.

Run directly to create the personal data folder and print where it is:
    python3 common.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import warnings
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
# Personal data lives outside the skill folder so skill updates never wipe it.
# STOCK_ANALYST_DATA overrides the location (tests use a temp folder).
DATA_DIR = Path(os.environ.get("STOCK_ANALYST_DATA", Path.home() / ".stock-analyst"))


def ensure_data_dir() -> Path:
    """Create the data folder and seed profile/lessons from templates if missing."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for tpl in (SKILL_DIR / "templates").glob("*.md"):
        target = DATA_DIR / tpl.name
        if not target.exists():
            shutil.copy(tpl, target)
    return DATA_DIR


def load_config() -> dict:
    """Default config, with the user's own overrides from DATA_DIR/config.json on top."""
    cfg = json.loads((SKILL_DIR / "config.json").read_text())
    override = DATA_DIR / "config.json"
    if override.exists():
        try:
            user = json.loads(override.read_text())
        except json.JSONDecodeError as e:
            raise ValueError(f"{override} is not valid JSON ({e}); fix or delete it to use defaults") from e
        for section, values in user.items():
            if isinstance(values, dict) and isinstance(cfg.get(section), dict):
                cfg[section].update(values)
            else:
                cfg[section] = values
    return cfg


def benchmark_for(ticker: str, asset_class: str | None = None) -> str | None:
    """What to compare a ticker against, or None to judge on its own (absolute) return.

    Stocks and equity funds use their market's index. Commodity funds (gold, oil)
    have no fair index, so they are judged on absolute return. A ticker is never
    compared with itself.
    """
    t = ticker.upper()
    local = t.endswith((".NS", ".BO", ".L"))
    if asset_class == "commodity":
        bench = None
    elif asset_class == "bond":
        bench = None if local else "AGG"  # US aggregate bond market
    elif asset_class == "crypto" or t.endswith("-USD"):
        bench = "BTC-USD"
    elif t.endswith((".NS", ".BO")):
        bench = "^NSEI"  # Nifty 50
    elif t.endswith(".L"):
        bench = "^FTSE"
    else:
        bench = "SPY"
    return None if bench == t else bench


def import_yfinance():
    """Import yfinance and hide the pandas deprecation warnings it triggers.

    The filter is added after the import because importing yfinance resets filters.
    """
    import logging

    import yfinance

    warnings.filterwarnings("ignore", module="yfinance")
    # yfinance logs "HTTP Error 404" when a ticker has no fundamentals (normal for ETFs).
    # Real failures still surface as exceptions or as notes in the output.
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    return yfinance


def latest_prices(tickers: list[str]) -> dict[str, float]:
    """Last close for each ticker. Raises if Yahoo returns nothing for any of them."""
    yf = import_yfinance()
    out = {}
    for t in tickers:
        close = yf.Ticker(t).history(period="5d", auto_adjust=True)["Close"].dropna()
        if close.empty:
            raise LookupError(f"No recent price for {t!r} from Yahoo Finance; check the symbol or try again later")
        out[t] = float(close.iloc[-1])
    return out


if __name__ == "__main__":
    path = ensure_data_dir()
    print(f"Data folder: {path}")
    for f in sorted(path.iterdir()):
        print(f"  {f.name}")
    sys.exit(0)
