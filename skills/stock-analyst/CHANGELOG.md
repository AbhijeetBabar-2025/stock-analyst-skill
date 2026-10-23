# Changelog

Every change to this skill's behaviour (weights, thresholds, workflow, scripts), newest first.

## 2026-10-23
- Dependencies: scripts require Python 3.11+, yfinance>=1.7, pandas>=3.1. Dashboard CDN libs
  updated (marked 18.1.1, DOMPurify 3.4.17, Phosphor 2.1.2) and pinned with SRI hashes; Phosphor
  now loads only the two styles used. Journal stat shows calls logged before the first review;
  gap above first-scan results.
- Dashboard Portfolio tab: add/remove holdings, totals per currency (no mixing), allocation
  bar, P&L, concentration warning, today's score per holding, click-through to analysis.
  Tidied controls: one button system, styled select, focus rings, spinner, 36px icon buttons.
- Dashboard analysis panel: click a card for why it's moving, Google News headlines,
  bull/bear cases, levels to watch, cautions, research gaps, learning-only trading
  practices (`scripts/brief.py`) and the newest saved report. Report mode now saves
  reports to `~/.stock-analyst/reports/TICKER-YYYY-MM-DD.md`. Scans add 1m/3m returns.
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
