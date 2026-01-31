---
name: worktree-gitignore-check
event: PreToolUse
tools:
  - Bash
---

# Worktree Gitignore Check

When the Bash command contains `git worktree add`, remind about the gitignore requirement.

## Detection Pattern

Check if the command matches:
- `git worktree add`

## When Triggered

Before executing, remind:

```
📋 Pre-worktree checklist:
   Ensure `.worktrees/` is in `.gitignore` to prevent committing nested repositories.

   Check: grep -q "^\.worktrees" .gitignore && echo "OK" || echo "Need to add"
```

## Why This Matters

Each worktree contains a complete checkout of the repository. Without gitignoring `.worktrees/`:
- You could accidentally commit nested copies of your entire codebase
- Git status becomes cluttered with thousands of "untracked" files
- Repository size balloons unnecessarily

## Recommended Fix

If not already gitignored:

```bash
echo ".worktrees/" >> .gitignore
git add .gitignore
git commit -m "chore: add .worktrees to gitignore"
```

## Keep It Brief

Don't block the command. Provide a brief reminder and proceed. The `/worktrees:new` skill handles this automatically, but direct `git worktree add` commands should still get a reminder.
