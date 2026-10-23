---
title: Troubleshooting
---

# Troubleshooting

Find the message you're seeing below.

## "command not found" or "is not recognized"

```text
zsh: command not found: npx
'uv' is not recognized as an internal or external command
```

The tool isn't installed, or your terminal hasn't noticed it yet.

1. **Close the terminal and open a new one.** This fixes it most of the time.
2. Still failing? Reinstall the tool: [Node.js (for `npx`)](./install/install-tools#install-nodejs), [uv](./install/install-tools#install-uv), or [Claude Code (for `claude`)](./install/install-claude-code).

## Claude doesn't know about the skill

1. Make sure you started Claude Code **after** installing the skill. Type `/exit` and run `claude` again.
2. Check it's installed:

   ```bash
   npx skills list -g
   ```

   You should see `stock-analyst`. If not, repeat [Install the skill](./install/install-skill).
3. You can also ask for it by name: *"Use the stock-analyst skill to score AAPL."*

## "No price history for …"

```text
✗ RELIANCE: No price history for 'RELIANCE'. Check the symbol …
```

The ticker is wrong. Indian stocks need `.NS` or `.BO` (`RELIANCE.NS`), and crypto needs `-USD` (`BTC-USD`). See [Tickers and markets](./guide/tickers).

## The first run is slow or seems stuck

The first time, `uv` downloads the data tools, which can take up to a minute. Later runs are fast. If it takes more than 3 minutes, check your internet connection and try again.

## Lots of "n/a" or "confidence low"

Yahoo Finance doesn't have full data for every stock, especially smaller companies and non-US markets. The score still works with what's available. A **full report** fills the gaps with web research.

## "Too Many Requests" or "rate limited"

Yahoo Finance limits how often you can fetch data. Wait a few minutes and try again, and avoid scoring dozens of stocks at once.

## Claude keeps asking for permission

When it asks, choose **"Yes, and don't ask again"** for the stock-analyst commands. To learn more about permissions, type `/permissions` inside Claude Code.

## Still stuck?

[Open an issue on GitHub](https://github.com/AbhijeetBabar-2025/stock-analyst-skill/issues). Include what you typed, what you expected, and the full message you saw.
