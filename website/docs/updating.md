---
title: Updating and uninstalling
---

# Updating and uninstalling

## Update to the latest version

1. Open a terminal and run:

   ```bash
   npx skills update stock-analyst -g -y
   ```

   You should see `✓ Updated stock-analyst`, or `All global skills are up to date` if you already have the latest version.

2. **Restart Claude Code** (type `/exit`, then `claude`) so it reads the new version of the skill.

3. **Using the dashboard?** Stop it with <kbd>Ctrl</kbd> + <kbd>C</kbd> in its terminal, start it again, and refresh the browser page:

   ```bash
   uv run ~/.claude/skills/stock-analyst/scripts/dashboard.py --open
   ```

Your journal, portfolio, profile, lessons, watchlist and saved reports are **kept**. They live outside the skill, in `~/.stock-analyst/`.

See what changed on the [What's new](./whats-new) page, or the detailed [changelog](https://github.com/AbhijeetBabar-2025/stock-analyst-skill/blob/main/skills/stock-analyst/CHANGELOG.md).

## How often should I update?

Once a month is plenty. Updates add features and fix bugs. They never change your saved data, and they never change any scoring weights you set yourself.

## See what's installed

```bash
npx skills list -g
```

## Uninstall

```bash
npx skills remove stock-analyst -g
```

If the dashboard is running, stop it first. This removes the skill but **keeps your data**. To delete your data too, delete the `~/.stock-analyst` folder.
