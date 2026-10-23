# Stock Analyst skill

A stock analyst skill for Claude Code and other AI agents. It learns how you invest and improves from its own track record.

- **Quick score:** a -100 to +100 score for any Yahoo Finance ticker (US, India `.NS`/`.BO`, London `.L`, crypto `-USD`). It combines 7 factors: valuation, growth, profitability, financial health, momentum, analyst views and earnings surprises.
- **Full report:** fundamental and technical research with bull and bear cases, valuation and risks, using live web research.
- **Comparison:** puts several tickers side by side and ranks them.
- **Portfolio tracker:** your holdings with profit/loss and warnings when one holding is too large.
- **Memory that improves over time:**
  - Every call goes into a journal.
  - After 30 days, *review* checks each call against what the stock and its market index actually did, and turns the misses into lessons.
  - The skill reads those lessons and your investor profile before every new analysis.
  - Factor weights can be re-tuned from the evidence, but only with your approval.

## Install

```bash
npx skills add AbhijeetBabar-2025/stock-analyst-skill
```

Add `-g` to install it for your user instead of the current project. Update later with `npx skills update`.

**Requirements:** [uv](https://docs.astral.sh/uv/getting-started/installation/), used to run the Python scripts. It installs `yfinance` and `pandas` automatically on first run. No API keys are needed.

## Use

Just ask your agent:

- "Quick score on NVDA and AMD"
- "Full report on RELIANCE.NS"
- "Compare MSFT vs GOOGL"
- "I bought 10 AAPL at 180"
- "Show my portfolio"
- "Review how our past calls did"

You can also run the scripts directly:

```bash
S=~/.claude/skills/stock-analyst   # or wherever the skill was installed
uv run $S/scripts/score.py AAPL TCS.NS BTC-USD
uv run $S/scripts/portfolio.py show
uv run $S/scripts/journal.py review
```

## Your data

Everything personal stays on your machine in `~/.stock-analyst/` (change the location with `STOCK_ANALYST_DATA`). Skill updates never touch it.

| File | What it holds |
|---|---|
| `profile.md` | How you invest, filled in as it comes up |
| `lessons.md` | What reviews and your corrections taught it |
| `journal.jsonl` | Every call: date, price, verdict, reason |
| `portfolio.json` | Your holdings |
| `config.json` | Your factor-weight overrides (optional) |
| `changes.md` | History of your tuning |

## How the score works

Each factor scores from -1 to +1, and the weighted total is scaled to -100…+100.

- **≥ 25:** BUY-lean
- **≤ -25:** SELL-lean
- **in between:** HOLD
- **BUY-lean with earnings under 14 days away:** becomes "HOLD (wait for earnings)"
- **Missing data:** lowers the confidence label; crypto gets momentum only and is marked "thin data"

Default weights are in [`config.json`](skills/stock-analyst/config.json).

## Development

```bash
uv run --with pytest pytest skills/stock-analyst/tests -q
python3 skills/stock-analyst/scripts/check_upstream.py   # did the borrowed sources change?
```

## Credits

- The report framework in `skills/stock-analyst/references/` comes from [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) under the MIT license (see `references/LICENSE-tradermonty`).
- The idea of a multi-factor quick score was inspired by [gracefullight/stock-checker](https://github.com/gracefullight/stock-checker). No code was copied from it.

## Disclaimer

This is a research tool, not financial advice. Data comes from Yahoo Finance and can be delayed, incomplete or wrong. Do your own research before investing.

## License

MIT
