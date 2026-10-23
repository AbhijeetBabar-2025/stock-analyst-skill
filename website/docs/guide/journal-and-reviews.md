---
title: Journal and reviews (how it learns)
---

# Journal and reviews: how it learns

This is what makes the skill get better the more you use it.

## The journal

Every time Claude scores or reports on a stock, it writes one line in your **journal**: the date, the price, the verdict, the score and a one-line reason.

```text
2026-10-23  AAPL     HOLD (wait for earnings)  @ 346.61  score +35  Strong margins, earnings in 10 days
```

See it any time:

```text
Show my stock journal
What did we say about AAPL before?
```

## Reviews

After a call is **30 days old**, it can be checked. Ask:

```text
Review how our past calls did
```

For each old call, Claude compares:

- how much the **stock** moved since the call, with
- how much the **market** moved over the same time (the S&P 500 for US stocks, the Nifty 50 for Indian stocks).

| Call | Counted as right when… |
|---|---|
| BUY-lean | the stock **beat** the market |
| SELL-lean | the stock **trailed** the market |
| HOLD | the stock stayed **within 3%** of the market |

You get a **hit rate**, for example "Hit rate: 7/10 (70%)".

## Lessons

Claude then looks for **patterns in the misses** and writes them down as lessons. For example:

> - 2026-12-01: Momentum-driven BUY calls on small caps failed 3 of 4 times. Be more careful with small caps. (evidence: journal ids …)

It **reads these lessons before every analysis**, so it doesn't repeat the same mistake.

## Tuning the score

When there's enough evidence (at least **5 reviewed calls**), Claude may suggest changing how much each factor counts. For example: *"Momentum misled us in 4 of 6 misses. Lower its weight from 20 to 15?"* It **only changes this if you say yes**, and it logs every change.

## Your profile

Claude also keeps a short **profile** of how you invest: your markets, how long you hold, your style, how long you like reports. It fills this in naturally as you chat. You never have to fill in a form. Want to set it straight away? Just say:

```text
I'm a long-term investor in Indian stocks, I like short reports
```

:::tip Make it a habit
Ask for a review **once a month**. The more calls are reviewed, the more useful the lessons become.
:::
