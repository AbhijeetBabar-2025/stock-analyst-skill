---
title: Updating and uninstalling
---

# Updating and uninstalling

## Update to the latest version

```bash
npx skills update stock-analyst -g -y
```

Your journal, portfolio, profile and lessons are **kept**. They live outside the skill, in `~/.stock-analyst/`.

See what changed in the [changelog](https://github.com/AbhijeetBabar-2025/stock-analyst-skill/blob/main/skills/stock-analyst/CHANGELOG.md).

## See what's installed

```bash
npx skills list -g
```

## Uninstall

```bash
npx skills remove stock-analyst -g
```

This removes the skill but **keeps your data**. To delete your data too, delete the `~/.stock-analyst` folder.
