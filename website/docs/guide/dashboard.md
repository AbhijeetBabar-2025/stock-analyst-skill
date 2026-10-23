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
4. Press **Details** for the key numbers behind the score.
5. Press **Log call** to save the call to your [journal](./journal-and-reviews).

Your list of symbols is saved automatically, so next time the dashboard scans them straight away. Use **Sort by** to order cards by score, momentum or symbol.

## Journal

The **Journal** tab lists every call, whether it was logged from the dashboard or by Claude:

- the price then and now, and the return since
- how the comparison index did over the same time
- the outcome: **right**, **wrong**, or **too early** (calls are checked after 30 days)
- your overall **hit rate**

## Good to know

- **It's private.** The dashboard only accepts connections from your own computer. Other devices and websites can't reach it.
- **Results are cached for 5 minutes**, so re-scanning doesn't hit Yahoo Finance again straight away.
- **Port already in use?** Start it on another port with `--port 8788`.
- **Light or dark?** It follows your system setting. Use the button in the top-right corner to switch.
