# Changelog

Every change to this skill's behaviour (weights, thresholds, workflow, scripts), newest first.

## 2026-10-23
- Dashboard: `scripts/dashboard.py` serves a local web UI (127.0.0.1:8787) to scan symbols
  as cards, save a watchlist, log calls and browse the journal with returns and outcomes.
- ETF support: funds are detected and scored on momentum, track record, risk, cost and
  liquidity (`etf_weights`). Comparison index follows asset class (commodities on absolute
  return, US bonds vs AGG). New ETF flags: leveraged/inverse, bear market, high fees, small
  fund, premium/discount to NAV. `journal.py add --benchmark`. A ticker is never compared
  with itself (BTC-USD, SPY).
- Published as a repo installable with `npx skills add`. Personal data moved to
  `~/.stock-analyst/` so updates never wipe it; user weight overrides go in its config.json.
- Created. Quick score (scripts/score.py, own code; multi-factor idea from gracefullight/stock-checker),
  report framework (references/, MIT, from tradermonty/claude-trading-skills),
  journal, portfolio tracker, lessons/profile memory, upstream checker.
