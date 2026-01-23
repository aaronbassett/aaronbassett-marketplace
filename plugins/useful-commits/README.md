# Useful Commits Plugin

A Claude Code plugin for crafting concise, conventional commit messages following the Conventional Commits specification with Angular convention.

## Overview

This plugin helps Claude generate better commit messages by enforcing:
- **Conventional Commits** format with Angular convention types
- **Strict formatting rules** (70 char subject limit, 90 char body wrap, imperative mood)
- **Concise, informative messages** that explain what and why
- **Breaking change notation** for API changes
- **Consistent scope usage** and proper structure

## Features

### Automatic Guidance
The `useful-commits` skill automatically activates when Claude detects commit-related work, providing:
- Conventional Commits structure and allowed types
- Character limits and formatting rules
- Imperative mood guidance
- Examples of good vs bad commits

### Manual Validation
Use the `/commit-message` command to explicitly validate or improve commit messages:
- Check messages against all rules
- Auto-fix common violations
- Generate messages from git diff

## Installation

1. Copy this plugin to your Claude Code plugins directory:
   ```bash
   cp -r useful-commits ~/.claude/plugins/
   ```

2. Restart Claude Code or start a new session

3. The plugin will automatically activate when working with git commits

## Usage

### Automatic Mode
Simply work with commits naturally:
```
You: "review all uncommitted changes and create relevant commits"
Claude: [Automatically applies useful-commits rules]
```

### Manual Validation
```bash
# Check a commit message
/commit-message check "feat: Added new feature."

# Auto-fix violations
/commit-message fix "feat: Added new feature."

# Generate from git diff
/commit-message suggest
```

## Components

- **Skill**: `useful-commits` - Auto-activates for commit operations
- **Command**: `/commit-message` - Manual validation and fixing

## Commit Message Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Allowed Types
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Test changes
- `build:` - Build system changes
- `ci:` - CI configuration changes
- `chore:` - Other changes that don't modify src or test files

### Key Rules
- Subject line max 70 characters (including type and scope)
- Use imperative mood ("add" not "added" or "adds")
- Don't capitalize subject line
- Don't end subject line with period
- Wrap body at 90 characters
- Body max 700 characters (excluding footers)
- Max 8 bullet points in body
- Breaking changes: use `!` after type/scope and `BREAKING CHANGE:` footer

## Examples

### Good Commits
```
feat(auth): add JWT token refresh mechanism

Implement automatic token refresh when tokens expire within 5 minutes
of API calls. This prevents users from being logged out during active
sessions.

BREAKING CHANGE: AuthService.login() now returns a Promise instead of
Observable
```

```
fix: prevent race condition in event handlers

Add mutex lock around event processing to ensure handlers execute
sequentially. Fixes issue where rapid events could trigger handlers
out of order.
```

### Bad Commits
```
feat: Added new feature.  ❌ (capitalized, ends with period)
Fix bug                   ❌ (not lowercase, missing type)
refactor: Refactored code ❌ (not imperative mood)
```

## License

MIT
