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

## ETFs and funds

An ETF (like **GLD**, **SPY** or **NIFTYBEES.NS**) is a basket of investments, not a company. It has no profits or analyst ratings, so it gets its own five factors:

| Factor | Weight | What it checks | Good sign |
|---|---|---|---|
| **Momentum** | 35 | Price trend, RSI, performance vs. its comparison index | Price above its 200-day average |
| **Track record** | 15 | Average yearly return over 3 and 5 years | 12-15%+ a year |
| **Risk** | 20 | How much the price swings, and how far it is below its 52-week high | Calm, close to its high |
| **Cost** | 15 | Expense ratio (the yearly fee), compared with similar funds | Under 0.10% a year |
| **Liquidity** | 15 | Fund size, and whether its price matches the value of what it holds (NAV) | Billions in assets, price within 0.2% of NAV |

**What each fund is compared against** depends on what it holds:

| Fund holds | Compared against |
|---|---|
| Shares (SPY, QQQ, NIFTYBEES.NS) | Its market index (S&P 500, Nifty 50) |
| US bonds (TLT, AGG) | AGG, the US bond market |
| Gold, silver, oil (GLD, GOLDBEES.NS) | Nothing: judged on its own return |
| Crypto (IBIT) | Bitcoin |

Extra ETF warnings:

| Flag | Meaning |
|---|---|
| ⚠ Leveraged or inverse fund | 2x, 3x or "short" funds reset daily and lose value over long holds |
| ⚠ Bear market | 20% or more below its 52-week high |
| ⚠ High expense ratio | Fees above 0.75% a year |
| ⚠ Small fund | Under 100M in assets: more likely to close, wider buy/sell gap |
| ⚠ Premium / discount to NAV | The price is more than 2% away from the value of its holdings |

:::note Indian ETFs
Yahoo Finance has no fund data (fees, size, track record) for Indian ETFs such as GOLDBEES.NS. They are scored on price trend and risk only, with low confidence. Check the expense ratio on the fund house's website.
:::

## Can I change the weights?

Yes. Just ask Claude, for example: *"I care less about analyst opinions, lower that weight to 5."* ETF weights work the same way, for example *"for ETFs, care more about cost"*. Your changes are saved in `~/.stock-analyst/config.json` and survive updates. Claude may also *suggest* changes after [reviews](./journal-and-reviews).
