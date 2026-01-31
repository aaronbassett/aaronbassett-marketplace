# CI Validation System Design

**Date:** 2026-01-26
**Status:** Approved
**Author:** Design session with user

## Overview

Add automated validation for plugins and marketplace using git hooks and GitHub Actions. The system validates plugin structure, JSON syntax, and marketplace completeness at three checkpoints: pre-commit (fast), pre-push (comprehensive), and CI (gatekeeper).

## Goals

- Catch validation errors before they reach remote repository
- Provide fast feedback during commits
- Ensure marketplace integrity before push
- Block invalid changes in CI regardless of bypassed hooks
- Work without Claude CLI authentication in CI environments

## Architecture

### Components

1. **scripts/ci/commit.sh** - Pre-commit validation
2. **scripts/ci/push.sh** - Pre-push validation
3. **scripts/ci/validate.sh** - Lightweight bash validator
4. **.lefthook.yml** - Git hooks configuration
5. **.github/workflows/validate.yml** - GitHub Actions workflow

### Validation Layers

```
Commit → Pre-commit Hook → Changed plugins only
  ↓
Push → Pre-push Hook → All plugins + marketplace
  ↓
Remote → GitHub Actions → All plugins + marketplace (CI gatekeeper)
```

## Component Details

### scripts/ci/commit.sh

Pre-commit validation that analyzes staged changes.

**Logic:**
1. Get staged files: `git diff --cached --name-only`
2. Extract unique plugin names from `plugins/*/` paths
3. Validate each affected plugin: `scripts/validate-plugin.sh <plugin>`
4. If `marketplace.json` staged: `scripts/validate-marketplace.sh --skip-plugins`
5. Exit with error code if any validation fails

**Characteristics:**
- Fast: validates only changed plugins (1-3 seconds per plugin)
- Smart: detects plugins from file paths
- Selective: marketplace validation only if staged
- Bypassable: `git commit --no-verify` works

**Exit Codes:**
- 0 = validation passed or no changes
- 1 = validation failed

### scripts/ci/push.sh

Pre-push comprehensive validation.

**Logic:**
1. Run `scripts/validate-marketplace.sh`
2. Exit with validation script's exit code

**Characteristics:**
- Comprehensive: validates all plugins + marketplace
- Simple: delegates to existing validate-marketplace.sh
- Slower: 5-15 seconds (acceptable for infrequent pushes)
- Final check: catches issues before remote

**Why validate everything:**
- Catches accumulated issues from multiple commits
- Ensures consistency after merges
- Safety net for `--no-verify` commits

### scripts/ci/validate.sh

Lightweight bash validator for CI (no Claude CLI dependency).

**Validation Checks:**

1. **JSON Syntax**
   - Parse marketplace.json with `jq`
   - Parse each plugin.json with `jq`
   - Fail on syntax errors

2. **Marketplace Completeness**
   - List all `plugins/*/` directories
   - Verify each plugin listed in marketplace.json `.plugins[]`
   - Check no extra/missing plugins

3. **Plugin Structure**
   - Each plugin has `.claude-plugin/` directory
   - Each plugin has `.claude-plugin/plugin.json`

4. **Required Fields**
   - marketplace.json: `plugins` array exists
   - plugin.json: `name`, `version`, `description` exist and non-empty

**Dependencies:**
- `jq` (JSON parsing)
- `bash` (existing scripts use it)
- `lib/colors.sh` (formatting)

**Output:**
- Clear error messages showing failures
- Summary count of issues
- Consistent formatting with existing scripts

**Usage Contexts:**
- GitHub Actions (primary use case)
- Local testing without Claude CLI
- Development validation

### .lefthook.yml

Git hooks configuration.

```yaml
pre-commit:
  commands:
    validate:
      run: scripts/ci/commit.sh

pre-push:
  commands:
    validate:
      run: scripts/ci/push.sh
```

**Team Workflow:**
1. Clone repository (lefthook.yml included)
2. Run `lefthook install` once
3. Hooks automatically run on commit/push
4. Bypass with `--no-verify` if needed

**Design Choices:**
- Uses `commands` (not `scripts`)
- Simple run configuration
- Version controlled for consistency
- Works with globally installed lefthook

### .github/workflows/validate.yml

GitHub Actions CI workflow.

**Triggers:**
```yaml
on:
  pull_request:
    branches: ['**']
  push:
    branches: [main, master]
```

**Job Steps:**
1. Checkout code
2. Setup environment (if needed for jq)
3. Run `bash scripts/ci/validate.sh`
4. Fail workflow if validation fails

**Characteristics:**
- No authentication required
- Works in forks
- Uses lightweight bash validation
- Same checks as pre-push but different script
- Cannot be bypassed

**Why not use Claude CLI:**
- Requires ANTHROPIC_API_KEY secret
- Authentication complexity in forks
- Bash validation is sufficient for CI

## Design Decisions

### Validation Strategy

**Question:** What should happen when validation finds issues?

**Decision:** Block with override option (B)

**Rationale:**
- Catches most issues early
- Allows emergency bypasses (`--no-verify`)
- GitHub Actions acts as final gatekeeper
- Balances safety with flexibility

### Pre-commit Scope

**Question:** What should pre-commit hook validate?

**Decision:** Validate entire plugin if any file changed (B), plus marketplace.json only if staged

**Rationale:**
- Plugin-level consistency matters
- Fast validation scripts make this practical
- Don't waste time on marketplace if unchanged
- Surgical approach for speed

### Pre-push Scope

**Question:** What should pre-push hook validate?

**Decision:** All plugins + marketplace (B)

**Rationale:**
- Pre-push is infrequent (acceptable slowness)
- Catches accumulated issues from multiple commits
- Safety net for `--no-verify` commits
- Ensures marketplace state is valid

### GitHub Actions Triggers

**Question:** When should CI validation run?

**Decision:** All PRs + commits to main/protected branches (C)

**Rationale:**
- Maximum coverage
- Validates all PRs regardless of target
- Protects main branch from direct pushes
- Feature branches validated by hooks anyway

### Lefthook Configuration

**Question:** How should lefthook be configured?

**Decision:** Create .lefthook.yml in repo (A)

**Rationale:**
- Consistent behavior across team
- Simple setup: `lefthook install`
- Version controlled configuration
- Easy to update for everyone

### CI Validation Approach

**Question:** Should CI use Claude CLI or bash validation?

**Decision:** Create lightweight bash validation script

**Rationale:**
- No authentication complexity
- Works in forks without secrets
- Sufficient validation for CI
- Local developers can still use Claude CLI

## Error Handling

### scripts/ci/commit.sh

- No staged changes → Exit 0 (allow commit)
- Files outside plugins/ → Ignore, extract only plugin paths
- marketplace.json changed but no plugins → Validate marketplace only
- Plugin directory deleted → Validation catches missing structure

### scripts/ci/push.sh

- No plugins directory → Fail with clear error
- Empty plugins directory → Pass (valid empty marketplace)

### scripts/ci/validate.sh

- jq not installed → Fail fast with installation instructions
- Malformed JSON → Report which file has syntax errors
- Plugin listed twice → Detect and report duplicate
- Missing .claude-plugin/ → Report missing structure
- Missing required fields → Show which plugin, which fields

### GitHub Actions

- Workflow fails → PR shows check failure
- Scripts not executable → Use `bash scripts/ci/validate.sh`
- Fork PRs → No secrets needed, validation works

### Bypass Handling

- Local hooks can be bypassed with `--no-verify`
- GitHub Actions cannot be bypassed (required check)
- README documents when bypassing is appropriate

## Documentation Updates

Add "Development" section to README:

```markdown
## Development

### Git Hooks Setup

This repository uses [lefthook](https://github.com/evilmartians/lefthook) for git hooks.

1. Check lefthook is installed: `lefthook --version`
2. Activate hooks: `lefthook install`
3. Hooks will now run automatically on commit and push

### Validation

**Automatic validation:**
- Pre-commit: Validates changed plugins
- Pre-push: Validates all plugins + marketplace

**Manual validation:**
- All plugins: `scripts/validate-marketplace.sh`
- Single plugin: `scripts/validate-plugin.sh <plugin-name>`
- CI validation: `scripts/ci/validate.sh`

**Bypassing hooks:**
Use `git commit --no-verify` or `git push --no-verify` when:
- Emergency hotfixes
- Documentation-only changes
- Hook issues need investigation

Note: GitHub Actions will still validate all changes.
```

## Implementation Checklist

- [ ] Create `scripts/ci/` directory
- [ ] Write `scripts/ci/commit.sh`
- [ ] Write `scripts/ci/push.sh`
- [ ] Write `scripts/ci/validate.sh`
- [ ] Create `.lefthook.yml`
- [ ] Create `.github/workflows/` directory
- [ ] Write `.github/workflows/validate.yml`
- [ ] Update README with development section
- [ ] Make scripts executable (`chmod +x`)
- [ ] Test pre-commit hook with plugin changes
- [ ] Test pre-commit hook with marketplace.json changes
- [ ] Test pre-push hook
- [ ] Test validate.sh independently
- [ ] Test GitHub Actions workflow
- [ ] Document bypass scenarios

## Dependencies

- **jq** - JSON parsing (already used in validate-marketplace.sh)
- **bash** - Shell scripting
- **lefthook** - Globally installed
- **Existing scripts:**
  - `scripts/validate-plugin.sh`
  - `scripts/validate-marketplace.sh`
  - `scripts/lib/colors.sh`
  - `scripts/lib/validation.sh`

## Future Enhancements

Not included in this design but potential future improvements:

- Caching validation results between pushes
- Parallel plugin validation for speed
- Pre-commit hook that validates only changed files (not full plugin)
- Validation severity levels (errors vs warnings)
- Auto-fix capabilities for common issues
