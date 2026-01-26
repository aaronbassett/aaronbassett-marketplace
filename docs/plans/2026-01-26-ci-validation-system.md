# CI Validation System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement automated validation for plugins and marketplace using git hooks and GitHub Actions to catch errors before they reach the remote repository.

**Architecture:** Three-layer validation system: pre-commit (fast, changed plugins only), pre-push (comprehensive, all plugins), and GitHub Actions (CI gatekeeper). Uses existing validate-plugin.sh/validate-marketplace.sh for local hooks, new lightweight bash validator for CI.

**Tech Stack:** Bash, jq, lefthook, GitHub Actions, existing validation library (lib/colors.sh, lib/json.sh, lib/validation.sh)

---

## Task 1: Create scripts/ci/validate.sh - Lightweight CI Validator

**Files:**
- Create: `scripts/ci/validate.sh`

**Step 1: Create scripts/ci directory**

Run: `mkdir -p scripts/ci`

Expected: Directory created.

**Step 2: Create the validate.sh script with shebang and setup**

```bash
#!/usr/bin/env bash
# validate.sh - Lightweight CI validation (no Claude CLI dependency)

set -euo pipefail

# Get script directory and source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/colors.sh"
source "$SCRIPT_DIR/../lib/json.sh"

# Default values
MARKETPLACE_JSON=".claude-plugin/marketplace.json"
PLUGINS_DIR="./plugins"
```

Expected: Script starts with proper bash setup and library sourcing.

**Step 3: Add dependency check for jq**

```bash
# Check for jq dependency
if ! command -v jq >/dev/null 2>&1; then
    print_error "jq is required but not installed"
    echo "Install with: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
fi
```

Expected: Script validates jq is available before proceeding.

**Step 4: Add JSON syntax validation function**

```bash
# Validate JSON syntax
validate_json_syntax() {
    local file="$1"
    local name="$2"

    if ! jq empty "$file" >/dev/null 2>&1; then
        print_error "Invalid JSON syntax in $name: $file"
        return 1
    fi
    return 0
}
```

Expected: Function returns 0 for valid JSON, 1 for invalid.

**Step 5: Add marketplace validation logic**

```bash
# Validation tracking
HAS_ERRORS=false

print_section "Validating marketplace.json"

# Check marketplace.json exists
if [[ ! -f "$MARKETPLACE_JSON" ]]; then
    print_error "Marketplace file not found: $MARKETPLACE_JSON"
    exit 1
fi

# Validate JSON syntax
if ! validate_json_syntax "$MARKETPLACE_JSON" "marketplace.json"; then
    HAS_ERRORS=true
fi

# Check required fields
if ! jq -e '.plugins' "$MARKETPLACE_JSON" >/dev/null 2>&1; then
    print_error "marketplace.json missing required field: plugins"
    HAS_ERRORS=true
fi
```

Expected: Validates marketplace.json exists, has valid JSON, and required fields.

**Step 6: Add plugin discovery and listing check**

```bash
print_section "Checking plugin completeness"

# Get plugins from filesystem
FILESYSTEM_PLUGINS=()
if [[ -d "$PLUGINS_DIR" ]]; then
    while IFS= read -r -d '' dir; do
        plugin_name=$(basename "$dir")
        FILESYSTEM_PLUGINS+=("$plugin_name")
    done < <(find "$PLUGINS_DIR" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
fi

# Get plugins from marketplace.json
MARKETPLACE_PLUGINS=()
while IFS= read -r source; do
    [[ -z "$source" ]] && continue
    plugin_name=$(basename "$source")
    MARKETPLACE_PLUGINS+=("$plugin_name")
done < <(jq -r '.plugins[]?.source // empty' "$MARKETPLACE_JSON" 2>/dev/null)

# Check for missing plugins (in filesystem but not marketplace)
for plugin in "${FILESYSTEM_PLUGINS[@]}"; do
    if [[ ! " ${MARKETPLACE_PLUGINS[@]} " =~ " ${plugin} " ]]; then
        print_error "Plugin exists in filesystem but not listed in marketplace: $plugin"
        HAS_ERRORS=true
    fi
done

# Check for extra plugins (in marketplace but not filesystem)
for plugin in "${MARKETPLACE_PLUGINS[@]}"; do
    if [[ ! " ${FILESYSTEM_PLUGINS[@]} " =~ " ${plugin} " ]]; then
        print_error "Plugin listed in marketplace but not found in filesystem: $plugin"
        HAS_ERRORS=true
    fi
done
```

Expected: Compares filesystem plugins vs marketplace listings, reports discrepancies.

**Step 7: Add plugin structure and validation loop**

```bash
print_section "Validating plugin structure"

SUCCESS_COUNT=0
FAILURE_COUNT=0

for plugin_name in "${FILESYSTEM_PLUGINS[@]}"; do
    plugin_path="$PLUGINS_DIR/$plugin_name"
    plugin_json="$plugin_path/.claude-plugin/plugin.json"

    # Check .claude-plugin directory exists
    if [[ ! -d "$plugin_path/.claude-plugin" ]]; then
        print_error "Plugin missing .claude-plugin directory: $plugin_name"
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        HAS_ERRORS=true
        continue
    fi

    # Check plugin.json exists
    if [[ ! -f "$plugin_json" ]]; then
        print_error "Plugin missing plugin.json: $plugin_name"
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        HAS_ERRORS=true
        continue
    fi

    # Validate JSON syntax
    if ! validate_json_syntax "$plugin_json" "$plugin_name/plugin.json"; then
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        HAS_ERRORS=true
        continue
    fi

    # Check required fields
    local missing_fields=()
    if ! jq -e '.name' "$plugin_json" >/dev/null 2>&1 || [[ $(jq -r '.name' "$plugin_json") == "null" ]]; then
        missing_fields+=("name")
    fi
    if ! jq -e '.version' "$plugin_json" >/dev/null 2>&1 || [[ $(jq -r '.version' "$plugin_json") == "null" ]]; then
        missing_fields+=("version")
    fi
    if ! jq -e '.description' "$plugin_json" >/dev/null 2>&1 || [[ $(jq -r '.description' "$plugin_json") == "null" ]]; then
        missing_fields+=("description")
    fi

    if [[ ${#missing_fields[@]} -gt 0 ]]; then
        print_error "Plugin $plugin_name missing required fields: ${missing_fields[*]}"
        FAILURE_COUNT=$((FAILURE_COUNT + 1))
        HAS_ERRORS=true
        continue
    fi

    print_success "Plugin validated: $plugin_name"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
done
```

Expected: Each plugin validated for structure, JSON syntax, required fields.

**Step 8: Add summary and exit logic**

```bash
# Print summary
echo ""
print_section "Summary"
print_info "Validated ${#FILESYSTEM_PLUGINS[@]} plugin(s): $SUCCESS_COUNT succeeded, $FAILURE_COUNT failed"

if [[ "$HAS_ERRORS" == "true" ]]; then
    print_error "Validation completed with errors"
    exit 1
else
    print_success "All validation checks passed"
    exit 0
fi
```

Expected: Clear summary showing validation results, appropriate exit code.

**Step 9: Make script executable**

Run: `chmod +x scripts/ci/validate.sh`

Expected: Script is now executable.

**Step 10: Test the validate.sh script**

Run: `bash scripts/ci/validate.sh`

Expected: Script runs, validates all plugins and marketplace, shows summary.

**Step 11: Commit**

```bash
git add scripts/ci/
git commit -m "feat: add lightweight CI validation script

- JSON syntax validation with jq
- Marketplace completeness checks
- Plugin structure validation
- Required fields validation
- No Claude CLI dependency for CI use"
```

Expected: Clean commit with validation script.

---

## Task 2: Create scripts/ci/commit.sh - Pre-commit Hook Script

**Files:**
- Create: `scripts/ci/commit.sh`

**Step 1: Create commit.sh with shebang and setup**

```bash
#!/usr/bin/env bash
# commit.sh - Pre-commit validation for changed plugins

set -euo pipefail

# Get script directory and source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/colors.sh"

print_section "Pre-commit validation"
```

Expected: Script setup with proper library sourcing.

**Step 2: Add staged files detection**

```bash
# Get staged files
STAGED_FILES=$(git diff --cached --name-only)

if [[ -z "$STAGED_FILES" ]]; then
    print_info "No staged changes detected"
    exit 0
fi
```

Expected: Script detects staged files or exits early if none.

**Step 3: Add plugin extraction logic**

```bash
# Extract unique plugin names from staged files
PLUGINS=()
while IFS= read -r file; do
    if [[ "$file" =~ ^plugins/([^/]+)/ ]]; then
        plugin="${BASH_REMATCH[1]}"
        # Add to array if not already present
        if [[ ! " ${PLUGINS[@]:-} " =~ " ${plugin} " ]]; then
            PLUGINS+=("$plugin")
        fi
    fi
done <<< "$STAGED_FILES"
```

Expected: Extracts unique plugin names from paths like `plugins/dev-specialisms/...`.

**Step 4: Add plugin validation loop**

```bash
# Validate changed plugins
VALIDATION_FAILED=false

if [[ ${#PLUGINS[@]} -gt 0 ]]; then
    print_info "Validating ${#PLUGINS[@]} plugin(s) with changes: ${PLUGINS[*]}"

    for plugin in "${PLUGINS[@]}"; do
        print_info "Validating plugin: $plugin"
        if ! "$SCRIPT_DIR/../validate-plugin.sh" "$plugin" --quiet; then
            print_error "Validation failed for plugin: $plugin"
            VALIDATION_FAILED=true
        fi
    done
else
    print_info "No plugin changes detected"
fi
```

Expected: Validates each changed plugin using existing validate-plugin.sh.

**Step 5: Add marketplace.json conditional validation**

```bash
# Check if marketplace.json is staged
if echo "$STAGED_FILES" | grep -q "^\.claude-plugin/marketplace\.json$"; then
    print_info "Validating marketplace.json"
    if ! "$SCRIPT_DIR/../validate-marketplace.sh" --skip-plugins --quiet; then
        print_error "Marketplace validation failed"
        VALIDATION_FAILED=true
    fi
fi
```

Expected: Validates marketplace.json only if it's in staged changes.

**Step 6: Add exit logic with bypass hint**

```bash
# Exit with appropriate code
if [[ "$VALIDATION_FAILED" == "true" ]]; then
    echo ""
    print_error "Pre-commit validation failed"
    print_info "Fix the issues above or use 'git commit --no-verify' to bypass"
    exit 1
fi

print_success "Pre-commit validation passed"
exit 0
```

Expected: Clear error message with bypass instructions, appropriate exit code.

**Step 7: Make script executable**

Run: `chmod +x scripts/ci/commit.sh`

Expected: Script is executable.

**Step 8: Test commit.sh with no staged changes**

Run: `bash scripts/ci/commit.sh`

Expected: Output shows "No staged changes detected", exits 0.

**Step 9: Test commit.sh with staged plugin changes**

```bash
# Stage a plugin file for testing
touch plugins/dev-specialisms/test.txt
git add plugins/dev-specialisms/test.txt
bash scripts/ci/commit.sh
git reset HEAD plugins/dev-specialisms/test.txt
rm plugins/dev-specialisms/test.txt
```

Expected: Script detects plugin change, validates dev-specialisms plugin.

**Step 10: Commit**

```bash
git add scripts/ci/commit.sh
git commit -m "feat: add pre-commit validation script

- Detects staged files
- Extracts changed plugins from file paths
- Validates only changed plugins
- Conditionally validates marketplace.json
- Provides bypass instructions on failure"
```

Expected: Commit successful with commit.sh script.

---

## Task 3: Create scripts/ci/push.sh - Pre-push Hook Script

**Files:**
- Create: `scripts/ci/push.sh`

**Step 1: Create push.sh script**

```bash
#!/usr/bin/env bash
# push.sh - Pre-push comprehensive validation

set -euo pipefail

# Get script directory and source libraries
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/colors.sh"

print_section "Pre-push validation"
print_info "Validating all plugins and marketplace..."

# Run comprehensive validation
if ! "$SCRIPT_DIR/../validate-marketplace.sh"; then
    echo ""
    print_error "Pre-push validation failed"
    print_info "Fix the issues above or use 'git push --no-verify' to bypass"
    exit 1
fi

print_success "Pre-push validation passed"
exit 0
```

Expected: Complete script that delegates to validate-marketplace.sh.

**Step 2: Make script executable**

Run: `chmod +x scripts/ci/push.sh`

Expected: Script is executable.

**Step 3: Test push.sh**

Run: `bash scripts/ci/push.sh`

Expected: Runs full marketplace validation, shows results.

**Step 4: Commit**

```bash
git add scripts/ci/push.sh
git commit -m "feat: add pre-push validation script

- Validates all plugins and marketplace
- Comprehensive check before push
- Provides bypass instructions on failure"
```

Expected: Commit successful with push.sh.

---

## Task 4: Create .lefthook.yml - Git Hooks Configuration

**Files:**
- Create: `.lefthook.yml`

**Step 1: Create lefthook configuration**

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

Expected: Lefthook config binds scripts to git hooks.

**Step 2: Commit lefthook configuration**

```bash
git add .lefthook.yml
git commit -m "feat: add lefthook git hooks configuration

- Pre-commit hook runs commit.sh validation
- Pre-push hook runs push.sh validation
- Team members activate with 'lefthook install'"
```

Expected: Lefthook config committed.

**Step 3: Install hooks locally for testing**

Run: `lefthook install`

Expected: Output shows hooks installed in .git/hooks/.

**Step 4: Test pre-commit hook**

```bash
# Make a change and try to commit
echo "# Test" > test-hook.txt
git add test-hook.txt
git commit -m "test: verify pre-commit hook"
```

Expected: Pre-commit validation runs, commit succeeds if no errors.

**Step 5: Clean up test commit**

```bash
git reset --soft HEAD~1
git reset HEAD test-hook.txt
rm test-hook.txt
```

Expected: Test commit removed, working directory clean.

---

## Task 5: Create .github/workflows/validate.yml - GitHub Actions Workflow

**Files:**
- Create: `.github/workflows/validate.yml`

**Step 1: Create workflows directory**

Run: `mkdir -p .github/workflows`

Expected: Directory created.

**Step 2: Create GitHub Actions workflow**

```yaml
name: Validate Plugins

on:
  pull_request:
    branches: ['**']
  push:
    branches:
      - main
      - master

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install jq
        run: sudo apt-get update && sudo apt-get install -y jq

      - name: Validate plugins and marketplace
        run: bash scripts/ci/validate.sh
```

Expected: Workflow file with proper triggers and validation steps.

**Step 3: Commit workflow**

```bash
git add .github/
git commit -m "feat: add GitHub Actions validation workflow

- Runs on all PRs and commits to main/master
- Uses lightweight bash validation (no auth needed)
- CI gatekeeper that cannot be bypassed"
```

Expected: Workflow committed successfully.

---

## Task 6: Update README.md - Development Documentation

**Files:**
- Modify: `README.md`

**Step 1: Read current README to find insertion point**

Run: `cat README.md | head -50`

Expected: View current README structure.

**Step 2: Add Development section to README**

Add this section (location depends on existing structure):

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

Expected: Development section added with clear instructions.

**Step 3: Commit README update**

```bash
git add README.md
git commit -m "docs: add development section with git hooks setup

- Lefthook installation instructions
- Validation commands (automatic and manual)
- Bypass instructions and when to use them
- Notes about CI enforcement"
```

Expected: README updated and committed.

---

## Task 7: Integration Testing

**Files:**
- None (testing existing code)

**Step 1: Test validate.sh directly**

Run: `bash scripts/ci/validate.sh`

Expected: All plugins validate successfully, exit code 0.

**Step 2: Test validate.sh with intentional error (temporarily break a plugin)**

```bash
# Break a plugin temporarily
mv plugins/dev-specialisms/.claude-plugin plugins/dev-specialisms/.claude-plugin.backup
bash scripts/ci/validate.sh || echo "Expected failure - exit code: $?"
mv plugins/dev-specialisms/.claude-plugin.backup plugins/dev-specialisms/.claude-plugin
```

Expected: Validation fails with clear error, exit code 1, directory restored.

**Step 3: Test commit.sh with plugin change**

```bash
echo "# Test" >> plugins/dev-specialisms/README.md
git add plugins/dev-specialisms/README.md
bash scripts/ci/commit.sh
git reset HEAD plugins/dev-specialisms/README.md
git checkout plugins/dev-specialisms/README.md
```

Expected: Validation runs for dev-specialisms plugin, changes reverted.

**Step 4: Test commit.sh with marketplace.json change**

```bash
# Make trivial change to marketplace.json
cp .claude-plugin/marketplace.json .claude-plugin/marketplace.json.backup
echo "" >> .claude-plugin/marketplace.json
git add .claude-plugin/marketplace.json
bash scripts/ci/commit.sh
mv .claude-plugin/marketplace.json.backup .claude-plugin/marketplace.json
git reset HEAD .claude-plugin/marketplace.json
```

Expected: Marketplace validation runs, file restored.

**Step 5: Test push.sh**

Run: `bash scripts/ci/push.sh`

Expected: Full validation runs, all plugins checked.

**Step 6: Test actual git commit with hooks**

```bash
echo "# Test hook" > test-integration.txt
git add test-integration.txt
git commit -m "test: integration test"
git reset --soft HEAD~1
git reset HEAD test-integration.txt
rm test-integration.txt
```

Expected: Pre-commit hook runs, commit succeeds, cleanup successful.

**Step 7: Verify lefthook status**

Run: `lefthook run pre-commit`

Expected: Shows pre-commit validation runs.

---

## Task 8: Final Review and Summary

**Files:**
- None (summary)

**Step 1: Review all changes**

Run: `git log --oneline --graph`

Expected: See all commits from this implementation.

**Step 2: Verify working directory is clean**

Run: `git status`

Expected: No uncommitted changes.

**Step 3: Test full workflow one final time**

```bash
# Test the whole flow
echo "# Final test" > final-test.txt
git add final-test.txt
git commit -m "test: final integration test"
# This should trigger pre-commit hook

# Cleanup
git reset --soft HEAD~1
git reset HEAD final-test.txt
rm final-test.txt
```

Expected: All hooks trigger properly, cleanup successful.

**Step 4: Document what was implemented**

Summary:
- scripts/ci/validate.sh - Lightweight CI validation
- scripts/ci/commit.sh - Pre-commit validation
- scripts/ci/push.sh - Pre-push validation
- .lefthook.yml - Hooks configuration
- .github/workflows/validate.yml - CI workflow
- README.md - Development documentation

All components tested and working.

---

## Implementation Complete

The CI validation system is now fully implemented with:

1. **Three validation layers:**
   - Pre-commit: Fast validation of changed plugins
   - Pre-push: Comprehensive validation of all plugins
   - GitHub Actions: CI enforcement that cannot be bypassed

2. **Two validation approaches:**
   - Local: Uses Claude CLI (validate-plugin.sh, validate-marketplace.sh)
   - CI: Uses bash + jq (validate.sh, no authentication needed)

3. **Team-friendly setup:**
   - One command to activate: `lefthook install`
   - Clear error messages with bypass instructions
   - Documented in README

4. **Safety features:**
   - Block-but-bypassable hooks for flexibility
   - GitHub Actions as final gatekeeper
   - Comprehensive error reporting

**Next steps:**
- Merge ci-validation branch to main
- Team members run `lefthook install`
- CI will automatically enforce on all PRs
