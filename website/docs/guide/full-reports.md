---
title: Full reports
---

# Full research reports

A deep dive, like a report from a stock analyst.

## How to ask

```text
Full report on Microsoft
Deep dive into RELIANCE.NS
Should I invest in Nvidia? Give me a detailed analysis
```

## What happens

1. Claude runs the [quick score](./quick-score) first to get the numbers.
2. It **searches the web** for the latest quarterly results, company guidance, news, analyst views and competitors.
3. It checks the web data against the script's numbers.
4. It writes the report using a professional template.

You may be asked to allow web searches. Say yes.

## What's in a report

| Section | What it tells you |
|---|---|
| **Executive summary** | The verdict in a few lines: rating, target price, conviction |
| **Company overview** | What the business does and how it makes money |
| **Bull case / bear case** | The best argument for and the best argument against |
| **Fundamentals** | Revenue, profits, cash flow and debt, and whether they're improving |
| **Valuation** | Whether the price is cheap or expensive compared with its history and its peers |
| **Technicals** | Trend, support and resistance levels, momentum |
| **Risks** | What could go wrong |
| **Catalysts** | Upcoming events that could move the price |

Every number comes with its **source and date**.

Each report is saved to `~/.stock-analyst/reports/` (for example `GLD-2026-10-23.md`). Open the [dashboard](./dashboard) and click the stock's card to read it again any time.

## Tips

- **Say how long you want it.** "Keep it to one page" or "be thorough". Claude remembers your preference in your [profile](../your-data).
- **Tell it your angle.** "I'm a long-term investor" or "I trade swings over a few weeks" changes what it focuses on.
- **Push back.** If you think something is wrong, say so. Claude records your correction as a **lesson** and takes it into account next time.
