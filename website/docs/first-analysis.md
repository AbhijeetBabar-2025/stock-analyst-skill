---
title: Your first analysis
---

# Your first analysis

Let's score a stock end to end. It takes about two minutes.

## 1. Start Claude Code

Open a terminal and type:

```bash
claude
```

## 2. Ask for a quick score

Type:

```text
Quick score on Apple
```

You don't need the ticker symbol (`AAPL`); Claude works it out. For Indian stocks you can say "Quick score on Reliance" too.

## 3. Allow the commands

Claude needs to run a small program to fetch stock prices. The first time, it **asks your permission** with a box like:

```text
Bash command
  uv run ~/.claude/skills/stock-analyst/scripts/score.py AAPL
Do you want to proceed?
❯ 1. Yes
  2. Yes, and don't ask again for this command
  3. No
```

Choose **1. Yes**. Choose **2** if you don't want to be asked every time.

:::note The first run is slower
The very first time, `uv` downloads the data tools it needs, which takes 20-60 seconds. After that, scores come back in a few seconds.
:::

## 4. Read the result

You'll get something like this (your numbers will be different):

```text
Apple Inc. (AAPL) · USD 346.61
Score +35/100 → HOLD (wait for earnings)  (confidence high, data coverage 100%)

Factors:
  valuation     -0.59 ██········
  growth        +0.68 ████████··
  profitability +1.00 ██████████
  health        +0.09 █████·····
  momentum      +0.62 ████████··
  analysts      -0.18 ████······
  earnings      +0.76 █████████·

Flags:
  ⚠ Earnings in 10 days: expect a big move either way
```

Claude then explains it in plain English. In short:

- **Score +35** leans positive. Anything at **+25 or above** counts as a "buy-lean".
- **But** earnings come out in 10 days, which can swing the price either way, so it says **wait**.
- The bars show *why*: very profitable and growing, but expensive (valuation is negative).

Want to understand every part? See [Understanding the score](./guide/understanding-the-score).

## 5. It remembers

Claude logs this call in your **journal** automatically. Next time you ask about Apple, it will remind you: *"Last time we scored it +35 at $346."* About a month later it can check whether the call was right. See [Journal and reviews](./guide/journal-and-reviews).

## Try these next

```text
Full report on Microsoft
```

```text
Compare TCS.NS and INFY.NS
```

```text
I bought 5 shares of NVDA at 180, add it to my portfolio
```

**Next:** dive into the [User guide](./guide/quick-score).
