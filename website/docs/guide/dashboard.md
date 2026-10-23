---
title: Dashboard
---

# Dashboard

Prefer clicking to typing? The skill includes a small web page that runs on your own computer. Type in symbols, press **Scan**, and each result appears as a card.

## Open it

The easiest way is to ask Claude:

```text
Open the stock dashboard
```

Or start it yourself in a terminal:

```bash
uv run ~/.claude/skills/stock-analyst/scripts/dashboard.py --open
```

Your browser opens **http://127.0.0.1:8787**. Leave the terminal open while you use it, and press <kbd>Ctrl</kbd> + <kbd>C</kbd> in the terminal to stop it.

## Scanner

1. Type a symbol (like `AAPL`, `GLD` or `RELIANCE.NS`) and press <kbd>Enter</kbd>. It becomes a chip. Add as many as you like, up to 20.
2. Press **Scan**.
3. Each stock or ETF gets a card showing:
   - its price and 6-month change
   - the **score gauge** and verdict (BUY-lean, HOLD or SELL-lean)
   - the **factor bars**, which show what pushed the score up or down
   - **warnings**, such as upcoming earnings or a bear market
4. **Click a card** to open its full analysis (see below).
5. Press **Log call** to save the call to your [journal](./journal-and-reviews).

Your list of symbols is saved automatically, so next time the dashboard scans them straight away. Use **Sort by** to order cards by score, momentum or symbol.

## The analysis panel

Click any card and a panel slides in from the right. Press <kbd>Esc</kbd>, the close button, or click outside it to close it.

| Section | What it tells you |
|---|---|
| **Summary** | The verdict and score in one line, and whether it's in an uptrend or downtrend |
| **Why it's moving** | The trend against its 50-day and 200-day averages, returns over 1, 3 and 6 months, how it compares with its index, distance from its 52-week high, RSI, and upcoming earnings |
| **Latest headlines** | News from the past 7 days, with links. Read these for the *story* behind the numbers |
| **Bull case / Bear case** | What's helping and hurting the score, with the actual figures |
| **What I'd watch** | Price levels (like the 50-day average or 52-week low) and dates (like earnings) that would change the picture, and what each would mean |
| **Cautions** | Warnings, how much data was missing, and the limits of the score |
| **Gaps in this research** | What this analysis didn't look at, so you know what to check yourself |
| **Trading practice notes** | General good habits that fit this situation, such as not chasing a stock after a big run or sizing down before earnings. **For learning only, not advice.** |
| **Key numbers** | The figures behind the score |
| **Full report** | Claude's latest full report on this stock, if you've asked for one |

:::tip Want the full report section filled in?
Ask Claude in Claude Code: `full report on GLD`. The report is saved automatically and appears in the panel the next time you open that card.
:::

:::note Where the "why" comes from
The panel's explanations are built from price and company data, so they describe *what* is happening (for example "in a downtrend, 26% below its high"). The *reasons* behind a move, like a news event or a rate decision, come from the headlines and from Claude's full report.
:::

## Journal

The **Journal** tab lists every call, whether it was logged from the dashboard or by Claude:

- the price then and now, and the return since
- how the comparison index did over the same time
- the outcome: **right**, **wrong**, or **too early** (calls are checked after 30 days)
- your overall **hit rate**

## Good to know

- **It's private.** The dashboard only accepts connections from your own computer. Other devices and websites can't reach it.
- **Results are cached for 5 minutes** (headlines for 15), so re-scanning doesn't hit Yahoo Finance or Google News again straight away.
- **Just updated the skill?** Stop the dashboard with <kbd>Ctrl</kbd> + <kbd>C</kbd>, start it again, and refresh the page.
- **Port already in use?** Start it on another port with `--port 8788`.
- **Light or dark?** It follows your system setting. Use the button in the top-right corner to switch.
