---
title: Quick score
---

# Quick score

A fast first look at any stock. It takes seconds.

## How to ask

Any of these work:

```text
Quick score on NVDA
How's Tesla looking?
Score AAPL, MSFT and GOOGL
Quick look at HDFC Bank
```

## What you get

- **A score from -100 to +100**, with a verdict: **BUY-lean**, **HOLD** or **SELL-lean**.
- **Confidence** (high, medium or low), which depends on how much data was available.
- **Seven factor bars** showing what pushed the score up or down.
- **Key numbers**: P/E, growth, margins, debt, RSI, moving averages, 52-week range, analyst target.
- **Flags**: warnings such as upcoming earnings, overbought conditions, heavy debt or losses.

When you score several stocks at once, you also get a **ranking**:

```text
Ranking: NVDA (+77) > MSFT (+67) > AAPL (+35)
```

## When to use it

- Narrowing down a list of ideas
- A daily or weekly check on stocks you're watching
- Deciding which stock deserves a [full report](./full-reports)

:::caution A score is not an answer
The quick score is a **screen**, like a doctor's quick check-up. It only uses numbers. It doesn't know about news, management changes or a new product. For real decisions, ask for a [full report](./full-reports).
:::

## Run it yourself (optional)

You can also run the scorer straight from a terminal without Claude:

```bash
uv run ~/.claude/skills/stock-analyst/scripts/score.py AAPL RELIANCE.NS
```

Add `--json` for machine-readable output.
