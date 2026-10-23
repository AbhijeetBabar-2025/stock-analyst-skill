---
name: stock-analyst
description: Use when the user asks to analyse, score, research, compare or get a report on a stock, ETF or crypto ticker, asks whether to buy, sell or hold something, wants to track their portfolio or past stock calls, or asks to review how earlier stock picks turned out.
---

# Stock Analyst

A personal stock analyst that gets better with use. It has a quick numeric score, a full research report, and a memory of who the user is, every call made, and what those calls taught us.

`$S` below is this skill's base directory. Scripts run with `uv run`, which installs yfinance on the fly (needs [uv](https://docs.astral.sh/uv/)). Tickers are Yahoo symbols: `AAPL`, `RELIANCE.NS`, `TCS.BO`, `BTC-USD`.

Personal data lives in `~/.stock-analyst/` (`$D`), outside the skill, so updates never wipe it. That folder holds `profile.md`, `lessons.md`, `journal.jsonl`, `portfolio.json`, `watchlist.json` (dashboard), optional `config.json` overrides and `changes.md`. On first use run `python3 $S/scripts/common.py` to create it.

## Every time: before and after

**Before:** read `$D/profile.md` and `$D/lessons.md`, and run `uv run $S/scripts/journal.py list TICKER` for past calls on this ticker. Let them shape the analysis (horizon, style, known blind spots). Mention a past call when one exists ("we said BUY-lean at 180 in March").

**After:** each analysis ends with these steps:
1. Log the call: `uv run $S/scripts/journal.py add TICKER --price P --verdict V --score S --benchmark B --source quick|report|comparison --thesis "one line"`. Take `B` from the score output's "log with --benchmark" line (`none` means judged on absolute return).
2. If the user revealed a preference or fact about how they invest, update `$D/profile.md`.
3. If the user corrected the analysis, add a dated bullet to `$D/lessons.md`.

## Pick the mode

| User asks | Mode |
|---|---|
| "quick look", "score", "how's X doing", several tickers | **Quick**: `uv run $S/scripts/score.py T1 [T2 ...]`, then explain the score in plain words |
| "full report", "deep dive", "should I invest" | **Report**: run Quick first, then follow `references/report-template.md` with web research |
| "compare X vs Y" | **Comparison**: Quick on all tickers, then the comparison structure in `references/report-template.md` |
| "my portfolio", "I bought ..." | `uv run $S/scripts/portfolio.py add/remove/show` |
| "show my journal", "what did we say about X" | `uv run $S/scripts/journal.py list [TICKER]` |
| "how did our calls do", "review" | **Review** (below) |
| "lower the weight of X", "I care less about Y" | Write just that change to `$D/config.json`, then log it in `$D/changes.md` |
| "open the dashboard", "show me in the browser" | Start `uv run $S/scripts/dashboard.py --open` in the background and give the user http://127.0.0.1:8787 (stop it when they're done) |
| "update the skill", "check for upstream changes" | **Upstream** (below) |

**Report mode details:** search the web for current price, latest quarterly results, guidance, news and peers; check them against the script's numbers. Read `references/fundamental-analysis.md`, `technical-analysis.md` and `financial-metrics.md` only as needed. Use the script's score as one input, and when your judgement differs from it, say so and explain why. Always cite sources with dates. Keep the report as long as the profile says the user likes.

## ETFs and funds

Detected automatically (Yahoo fund type, or "ETF"/"BEES" in the name for Indian ETFs) and scored on fund factors instead of company ones: momentum, track record (3y/5y returns), risk (volatility, distance from high), cost (expense ratio vs category) and liquidity (assets, price vs NAV). Comparison index follows the asset class: equity funds vs their market index, US bond funds vs AGG, gold and other commodities on absolute return.

In Report mode, research what drives the asset, not the fund: gold (real yields, dollar, central-bank buying), bonds (rates, inflation), equity funds (index valuation, top holdings). Name cheaper or bigger alternatives tracking the same thing (e.g. GLDM vs GLD). Indian ETFs have no fund data on Yahoo, so get the expense ratio and tracking error from the fund house.

## Getting better over time

**Review** (offer it when the journal has calls older than 30 days and none were reviewed this month):
1. `uv run $S/scripts/journal.py review` checks each old call against the price and the benchmark since.
2. Look for patterns in the misses (one factor keeps misleading, a sector we misjudge, calls made just before earnings).
3. Write each pattern as a lesson in `$D/lessons.md`, citing journal ids.
4. If a factor weight or threshold looks wrong, propose the change with the evidence. Apply it only after the user agrees, by writing just the changed keys to `$D/config.json` (e.g. `{"weights": {"momentum": 15}}`). Never edit `$S/config.json`; it holds the defaults. Then log the change with its date and reason in `$D/changes.md`.

Don't change weights on fewer than 5 reviewed calls; that's noise.

**Upstream** (maintainers, working in the repo checkout): `python3 $S/scripts/check_upstream.py`. For changed tradermonty files, diff them against `references/` and merge what's useful. They're MIT-licensed, so keep `references/LICENSE-tradermonty`. For gracefullight, take ideas only: its repo has no license, so never copy its code. Reimplement good ideas in `scripts/scoring.py` with a test. Afterwards run `check_upstream.py --accept` and add a line to `CHANGELOG.md`.

**Changing the scripts** (maintainers): add or adjust a test in `$S/tests/` and run `uv run --with pytest pytest $S/tests -q`.

## Reading the score

The composite runs from -100 to +100. Stocks use 7 factors (valuation, growth, profitability, health, momentum, analysts, earnings), each scored -1 to +1. ≥25 is BUY-lean, ≤-25 is SELL-lean, anything between is HOLD. ETFs use the 5 fund factors above, weighted by `etf_weights`. A BUY-lean becomes "HOLD (wait for earnings)" when earnings are less than 14 days away. Confidence drops when data is missing. Yahoo has thin data for many non-US stocks, so for those lean on web research.

## Common mistakes

- Treating the score as the answer. It's a screen; the report is the analysis.
- Skipping the journal entry. Without it, Review has nothing to learn from.
- Quizzing the user about their profile upfront. Fill gaps as they come up.
- Using an Indian ticker without `.NS`/`.BO`.

End analyses with one line: this is research, not financial advice.
