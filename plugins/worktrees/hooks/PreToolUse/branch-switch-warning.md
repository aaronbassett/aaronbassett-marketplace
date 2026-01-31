---
name: worktree-branch-switch-warning
event: PreToolUse
tools:
  - Bash
---

# Worktree Branch Switch Warning

When the Bash command contains `git checkout` or `git switch` (without `-b` flag for creating new branches), provide a brief warning about worktree awareness.

## Detection Pattern

Check if the command matches:
- `git checkout <branch>` (not `git checkout -b`)
- `git switch <branch>` (not `git switch -c`)

## When Triggered

Briefly mention:

```
⚠️ Branch switch detected. If using worktrees, verify this won't conflict with active worktrees.
Run `git worktree list` to check.
```

## When NOT to Warn

- `git checkout -b <new-branch>` - Creating new branch is fine
- `git switch -c <new-branch>` - Creating new branch is fine
- `git checkout -- <file>` - File checkout, not branch switch
- `git checkout .` - Discarding changes, not branch switch

## Keep It Brief

Don't block the command. Just provide a one-line reminder and proceed with execution.
