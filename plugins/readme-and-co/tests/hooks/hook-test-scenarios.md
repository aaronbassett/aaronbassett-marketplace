# Hook Test Scenarios

This document describes test scenarios for the doc-update-check PostToolUse hook.

## Test 1: Hook Triggers on package.json Edit

**Setup:**
- No config file exists (hook enabled by default)

**Action:**
```bash
echo '{"version": "2.0.0", "dependencies": {"express": "^4.18.0"}}' > package.json
```

**Expected Hook Behavior:**
The hook should suggest:
```
💡 package.json modified. Consider updating:
   • README.md - Verify installation instructions reflect new dependencies
   • CHANGELOG.md - If version changed, document the changes
```

## Test 2: Hook Triggers on New Source File

**Setup:**
- No config file exists (hook enabled by default)

**Action:**
```bash
cat > src/auth.ts << 'EOFILE'
export function authenticate(token: string) {
  // Implementation
}
EOFILE
```

**Expected Hook Behavior:**
The hook should suggest:
```
💡 New TypeScript file created (src/auth.ts). Consider updating:
   • README.md - Document the new authentication feature
   • README.md - Add authentication to the Features section
```

## Test 3: Hook is Disabled via Config

**Setup:**
- Create config with hook disabled:
```yaml
---
hooks:
  doc_updates:
    enabled: false
---
```

**Action:**
```bash
echo '{"version": "3.0.0"}' > package.json
```

**Expected Hook Behavior:**
The hook should NOT provide any suggestions (disabled).

## Test 4: Hook Triggers on CI/CD Config Change

**Setup:**
- No config file exists

**Action:**
```bash
mkdir -p .github/workflows
cat > .github/workflows/ci.yml << 'EOFILE'
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
EOFILE
```

**Expected Hook Behavior:**
The hook should suggest:
```
💡 CI/CD configuration modified. Consider updating:
   • CONTRIBUTING.md - Update CI/CD section if workflow changed
   • README.md - Update badges if new workflows added
```

## Test 5: Hook Does NOT Trigger on Documentation File

**Setup:**
- No config file exists

**Action:**
```bash
echo "# New Section" >> README.md
```

**Expected Hook Behavior:**
The hook should NOT provide suggestions (already updating documentation).

## Test 6: Hook Triggers on Test File Modification

**Setup:**
- No config file exists

**Action:**
```bash
cat > tests/auth.test.ts << 'EOFILE'
import { authenticate } from '../src/auth';

test('authenticate validates token', () => {
  // Test implementation
});
EOFILE
```

**Expected Hook Behavior:**
The hook should suggest:
```
💡 Test files modified. Consider updating:
   • CONTRIBUTING.md - Ensure testing documentation matches current test setup
   • README.md - Update testing section if test commands changed
```

## Test 7: Multiple Triggers in One Session

**Setup:**
- No config file exists

**Action:**
```bash
echo '{"dependencies": {"axios": "^1.0.0"}}' > package.json
cat > src/api.ts << 'EOFILE'
export function fetchData() {}
EOFILE
```

**Expected Hook Behavior:**
The hook should combine suggestions:
```
💡 Significant changes detected. Consider updating documentation:
   • README.md - Verify installation instructions (dependencies changed)
   • README.md - Document new functionality (new source files added)
   • CHANGELOG.md - Document version changes if applicable
```

## Verification Checklist

For each test scenario:

- [ ] Hook file exists at `hooks/PostToolUse/doc-update-check.md`
- [ ] Hook frontmatter is valid (name, event, tools)
- [ ] Config file parsing works correctly
- [ ] Hook respects `enabled: false` setting
- [ ] Suggestions are clear and actionable
- [ ] Hook doesn't trigger on inappropriate files
- [ ] Hook doesn't trigger when disabled

## Manual Testing

Since hooks execute as Claude Code instructions, manual testing involves:

1. Ensuring the hook file is in the correct location
2. Verifying the frontmatter format
3. Checking that configuration parsing logic is correct
4. Confirming suggestion patterns match file types

The actual hook execution will happen when Claude Code processes PostToolUse events.
