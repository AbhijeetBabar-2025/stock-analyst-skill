---
title: Tickers and markets
---

# Tickers and markets

A **ticker** is a stock's short code, like `AAPL` for Apple. The skill uses **Yahoo Finance** tickers. You can usually just say the company name and Claude will find the ticker, but here is how they work.

## By market

| Market | Format | Examples | Compared against | How well it works |
|---|---|---|---|---|
| **US** | Plain symbol | `AAPL`, `MSFT`, `NVDA` | S&P 500 (SPY) | Best: all data available |
| **India, NSE** | Add `.NS` | `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS` | Nifty 50 | Good |
| **India, BSE** | Add `.BO` | `RELIANCE.BO`, `TCS.BO` | Nifty 50 | Good |
| **UK** | Add `.L` | `HSBA.L`, `BP.L` | FTSE 100 | Good |
| **Crypto** | Add `-USD` | `BTC-USD`, `ETH-USD` | Bitcoin | Price trend only |
| **Other** | Yahoo suffix | `7203.T` (Tokyo), `SAP.DE` (Germany) | S&P 500 | Varies |

ETFs use the same formats (`GLD`, `SPY`, `GOLDBEES.NS`, `NIFTYBEES.NS`). They're detected automatically and scored differently from companies. See [ETFs and funds](./understanding-the-score#etfs-and-funds).

## Finding a ticker

1. Go to [finance.yahoo.com](https://finance.yahoo.com).
2. Search for the company name.
3. The ticker is the code in brackets, e.g. **Reliance Industries Limited (RELIANCE.NS)**.

## Things to know

- **Indian stocks need `.NS` or `.BO`.** Plain `RELIANCE` won't work.
- **Crypto has no company data** (no profits or debt), so only the price trend is scored and the result is marked **"thin data"**.
- **Smaller markets and smaller companies** often have gaps in their data. The confidence level tells you how much data was missing.
