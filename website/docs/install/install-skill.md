---
title: 4. Install the skill
---

# Step 4: Install the Stock Analyst skill

This is the easy part: one command.

:::info Already installed?
You don't need to install again. Update to the latest version instead:

```bash
npx skills update stock-analyst -g -y
```

Your journal, portfolio and reports are kept. See [What's new](../whats-new) for the changes.
:::

## Install

Paste this into your terminal:

```bash
npx skills add AbhijeetBabar-2025/stock-analyst-skill -g -a claude-code -y
```

What each part means (you don't need to remember this):

| Part | Meaning |
|---|---|
| `npx skills add` | "Download and install a skill" |
| `AbhijeetBabar-2025/stock-analyst-skill` | Where the skill lives on GitHub |
| `-g` | Install it for your user account, so it works in every folder |
| `-a claude-code` | Install it for Claude Code |
| `-y` | Don't ask me to confirm, just do it |

If it asks `Need to install the following packages: skills… Ok to proceed?`, type `y` and press <kbd>Enter</kbd>.

You should end with a message like:

```text
✓ stock-analyst (copied)
  → ~/.claude/skills/stock-analyst
Done!
```

:::tip Using a different AI assistant?
The skill also works with other assistants that support skills. Leave out `-a claude-code -y` and the installer will ask which assistant to install it for:

```bash
npx skills add AbhijeetBabar-2025/stock-analyst-skill -g
```
:::

## Check it worked

1. Open a **new** terminal and start Claude Code:

   ```bash
   claude
   ```

2. Type this and press <kbd>Enter</kbd>:

   ```text
   What skills do you have for stocks?
   ```

3. Claude should mention **stock-analyst**.

If it doesn't, see [Troubleshooting](../troubleshooting#claude-doesnt-know-about-the-skill).

**Next:** [Your first analysis →](../first-analysis)
