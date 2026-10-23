---
title: What's new
---

# What's new

The latest changes, newest first. Already installed? [Update in one command](./updating).

## October 2026

### Portfolio tab in the dashboard

Add, view and remove holdings in the [dashboard](./guide/dashboard#portfolio). It shows totals per currency, an allocation bar, profit and loss, a warning when one holding gets too big, and today's score for each holding. Click a holding for its full analysis. The buttons, dropdowns and focus outlines across the dashboard were also tidied up.

### Analysis panel in the dashboard

Click any card in the [dashboard](./guide/dashboard) to open a full analysis:

- **Why it's moving:** trend, recent returns, distance from the high, RSI and upcoming earnings, in plain words
- **Latest headlines** from the past 7 days, with links
- **Bull case and bear case**, built from what is helping and hurting the score
- **What I'd watch:** price levels and dates that would change the picture
- **Cautions** and **gaps in this research**
- **Trading practice notes**, for learning only
- **Claude's full report**, if you've asked for one

Full reports are now saved automatically to `~/.stock-analyst/reports/`, so the panel can show them.

### Dashboard

A local web page to scan symbols, see the results as cards, keep a watchlist, log calls and follow your journal. See [Dashboard](./guide/dashboard).

### ETF support

ETFs such as **GLD**, **SPY**, **TLT** and **NIFTYBEES.NS** are detected automatically and scored on fund factors: momentum, track record, risk, cost and liquidity. Each is compared with the right index for what it holds; gold is judged on its own return. See [ETFs and funds](./guide/understanding-the-score#etfs-and-funds).

### First release

Quick scores, full reports, comparisons, a portfolio tracker, and a journal that learns from its past calls.

:::tip After updating
If the dashboard is running, stop it (<kbd>Ctrl</kbd> + <kbd>C</kbd> in its terminal) and start it again to load the new version. Refresh the browser page too.
:::
