import importlib
import sys
from argparse import Namespace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture
def mods(tmp_path, monkeypatch):
    """Reload the scripts so they write to a temp data folder, not real data."""
    monkeypatch.setenv("STOCK_ANALYST_DATA", str(tmp_path))
    import common
    import journal
    import portfolio

    for m in (common, journal, portfolio):
        importlib.reload(m)
    return journal, portfolio


def test_judge(mods):
    journal, _ = mods
    assert journal.judge("BUY-lean", 0.10, 0.05) == "right"
    assert journal.judge("BUY-lean", 0.04, 0.05) == "wrong"
    assert journal.judge("SELL-lean", -0.10, 0.02) == "right"
    assert journal.judge("HOLD", 0.06, 0.05) == "right"
    assert journal.judge("HOLD", 0.20, 0.05) == "wrong"
    assert journal.judge("HOLD (wait for earnings)", 0.0, None) == "right"


def test_journal_add_and_list(mods, capsys):
    journal, _ = mods
    journal.cmd_add(Namespace(ticker="aapl", price=200.0, verdict="BUY-lean", score=30.0,
                              target=None, source="quick", thesis="test"))
    entries = journal.load()
    assert len(entries) == 1
    assert entries[0]["ticker"] == "AAPL" and entries[0]["benchmark"] == "SPY"
    journal.cmd_list(Namespace(ticker="AAPL"))
    assert "BUY-lean" in capsys.readouterr().out


def test_benchmark_for_indian_ticker(mods):
    import common
    assert common.benchmark_for("RELIANCE.NS") == "^NSEI"
    assert common.benchmark_for("BTC-USD") == "BTC-USD"


def test_portfolio_average_cost_and_remove(mods):
    _, portfolio = mods
    h = portfolio.add({}, "aapl", 10, 100)
    h = portfolio.add(h, "AAPL", 10, 200)
    assert h["AAPL"] == {"qty": 20, "avg_cost": 150.0}
    h = portfolio.remove(h, "AAPL", 5)
    assert h["AAPL"]["qty"] == 15
    h = portfolio.remove(h, "AAPL", None)
    assert "AAPL" not in h
    with pytest.raises(KeyError):
        portfolio.remove(h, "MSFT", None)


def test_data_dir_seeded_from_templates(mods, tmp_path):
    import common
    common.ensure_data_dir()
    assert (tmp_path / "profile.md").exists() and (tmp_path / "lessons.md").exists()
    (tmp_path / "profile.md").write_text("mine")
    common.ensure_data_dir()  # must not overwrite the user's edits
    assert (tmp_path / "profile.md").read_text() == "mine"


def test_user_config_overrides_defaults(mods, tmp_path):
    import common
    (tmp_path / "config.json").write_text('{"weights": {"momentum": 5}}')
    cfg = common.load_config()
    assert cfg["weights"]["momentum"] == 5
    assert cfg["weights"]["growth"] == 15  # untouched defaults stay


def test_bad_user_config_has_clear_error(mods, tmp_path):
    import common
    (tmp_path / "config.json").write_text("{oops")
    with pytest.raises(ValueError, match="not valid JSON"):
        common.load_config()
