---
title: Understanding the score
---

# Understanding the score

## The big number

The score runs from **-100** (very weak) to **+100** (very strong).

| Score | Verdict | Meaning |
|---|---|---|
| **+25 or higher** | BUY-lean | The numbers look good overall |
| **between -25 and +25** | HOLD | Mixed: nothing compelling either way |
| **-25 or lower** | SELL-lean | The numbers look weak overall |

Special cases:

- **HOLD (wait for earnings).** The score would be a BUY-lean, but the company reports results within 14 days. Results can move a stock 10% or more overnight, so waiting is usually wiser.
- **(thin data).** Less than 40% of the data was available, e.g. for crypto. Trust it less.

## The seven factors

Each factor gets a mini-score from **-1** (bad) to **+1** (good). They're blended using weights:

| Factor | Weight | What it checks | Good sign |
|---|---|---|---|
| **Valuation** | 15 | P/E ratio and PEG: how expensive the stock is compared with its profits | Low P/E (around 12 or less) |
| **Growth** | 15 | How fast sales and profits are growing | 25%+ sales growth |
| **Profitability** | 15 | Profit margin and return on equity | 25%+ margins |
| **Health** | 10 | Debt, short-term cash cushion, free cash flow | Low debt, positive cash flow |
| **Momentum** | 20 | Price trend vs. moving averages, RSI, and performance vs. the market | Price above its 200-day average, beating the market |
| **Analysts** | 15 | Professional analysts' ratings and price targets | Strong buy ratings, target well above price |
| **Earnings** | 10 | Did the company beat profit forecasts recently? | Beat expectations 4 quarters in a row |

New to these terms? See the [Glossary](../glossary).

## Confidence

- **High:** 85%+ of the data was available.
- **Medium:** 60-85%.
- **Low:** under 60%. Factors with no data are left out, not counted as zero.

## Flags

| Flag | Meaning |
|---|---|
| ⚠ Earnings in N days | Big move expected either way |
| ⚠ Overbought | RSI over 70 and near the 52-week high, so it may have run too far, too fast |
| ⚠ High leverage | Debt is more than twice the company's equity |
| ⚠ Loss-making | The company lost money over the past year |
| ⚠ Fewer than 3 analysts | Too little professional coverage to trust the analyst factor |

## Can I change the weights?

Yes. Just ask Claude, for example: *"I care less about analyst opinions, lower that weight to 5."* Your changes are saved in `~/.stock-analyst/config.json` and survive updates. Claude may also *suggest* changes after [reviews](./journal-and-reviews).
