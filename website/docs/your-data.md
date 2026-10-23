---
title: Your data and privacy
---

# Your data and privacy

Everything personal is stored **only on your computer**, in a folder called `.stock-analyst` in your home folder:

- **Mac / Linux:** `~/.stock-analyst/`
- **Windows:** `C:\Users\<your name>\.stock-analyst\`

| File | What's in it |
|---|---|
| `profile.md` | How you invest: markets, style, horizon, preferences |
| `lessons.md` | What reviews and your corrections taught it |
| `journal.jsonl` | Every call: date, price, verdict, reason |
| `portfolio.json` | Your holdings |
| `watchlist.json` | Symbols saved in the dashboard |
| `reports/` | Full reports Claude wrote, one Markdown file per ticker and date |
| `config.json` | Your custom factor weights (only if you changed any) |
| `changes.md` | A history of weight changes |

## Good to know

- **Updates never touch this folder.** It's kept separate from the skill on purpose.
- **You can read and edit these files** with any text editor. `profile.md` and `lessons.md` are plain text.
- **Back it up** by copying the folder somewhere safe.
- **Start fresh** by deleting the folder. It's recreated automatically, empty.
- **Move it** by setting the environment variable `STOCK_ANALYST_DATA` to another folder path.

## What leaves your computer?

- **Ticker symbols** are sent to Yahoo Finance to fetch prices. Your holdings and quantities are not sent.
- **Your conversation** with Claude goes to Anthropic, as with any Claude conversation. Claude reads your profile, lessons and journal to tailor its answers.
- **Web searches** for full reports go through Claude's web search tool.
