---
title: Portfolio tracker
---

# Portfolio tracker

Keep track of what you own and how it's doing.

## Add what you bought

Just tell Claude:

```text
I bought 10 shares of AAPL at 180
Add 5 RELIANCE.NS at 1250 to my portfolio
```

Bought the same stock again at a different price? Add it again. The tracker works out your **average cost** automatically.

## See how you're doing

```text
Show my portfolio
```

```text
ticker      qty   avg cost     price      value     P&L   weight
AAPL         10     180.00    346.48   3,464.85   92.5%   76.8%  ⚠ concentrated
MSFT          2     400.00    524.48   1,048.96   31.1%   23.2%

Total value 4,513.81 · cost 3,300.00 · P&L +36.8%
```

- **P&L** is profit or loss as a percentage.
- **Weight** is how much of your portfolio this stock makes up.
- **⚠ concentrated** means one stock is more than 30% of your portfolio. If it falls sharply, your whole portfolio suffers.

## Sold something?

```text
I sold 5 AAPL
I sold all my MSFT
```

:::note Mixed currencies
Each stock is shown in its own currency (USD for AAPL, INR for RELIANCE.NS). If you hold stocks from different countries, the **total** adds the numbers as-is without converting currencies, so treat it as rough.
:::

:::info Your holdings are private
Your portfolio is saved only on your computer, in `~/.stock-analyst/portfolio.json`. It is never uploaded anywhere. The tracker isn't connected to your broker, so it only knows what you tell it.
:::
