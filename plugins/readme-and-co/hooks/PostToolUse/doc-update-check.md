---
name: doc-update-check
event: PostToolUse
tools:
  - Write
  - Edit
---

# Documentation Update Check Hook

**IMPORTANT**: Before providing suggestions, check if this hook is enabled in `.claude/readme-and-co.local.md`:

1. Check if `.claude/readme-and-co.local.md` exists
2. If it exists, read the YAML frontmatter
3. If `hooks.doc_updates.enabled` is set to `false`, **stop here and do nothing**
4. If enabled (or not specified), proceed with suggestions below

## When to Suggest Documentation Updates

After using Write or Edit tools, check the modified file path and suggest documentation updates based on these patterns:

### Dependency/Package Files Modified

**Files**: `package.json`, `pyproject.toml`, `Cargo.toml`, `Gemfile`, `go.mod`, `requirements.txt`, `Pipfile`

**Suggest**:
```
💡 Dependency file modified. Consider updating:
   • README.md - Verify installation instructions reflect new dependencies
   • README.md - Update prerequisites if minimum versions changed
```

**Additional for package.json**:
```
   • CHANGELOG.md - If version changed, document the changes
```

### New Source Files Created (Write tool only)

**Files**: `*.py`, `*.js`, `*.ts`, `*.tsx`, `*.jsx`, `*.rs`, `*.go` (and tool was Write, not Edit)

**Suggest**:
```
💡 New source file added. Consider updating:
   • README.md - Document new features or functionality in Usage section
   • README.md - Add to Features list if it's a significant addition
```

### CI/CD Configuration Changed

**Files**: `.github/workflows/*`, `.gitlab-ci.yml`, `.circleci/*`, `Jenkinsfile`

**Suggest**:
```
💡 CI/CD configuration modified. Consider updating:
   • CONTRIBUTING.md - Update CI/CD section if workflow changed
   • README.md - Update badges if new workflows added
```

### Test Files Modified

**Files**: `test_*.py`, `*_test.go`, `*.test.ts`, `*.test.js`, `*.spec.ts`, `*.spec.js`

**Suggest**:
```
💡 Test files modified. Consider updating:
   • CONTRIBUTING.md - Ensure testing documentation matches current test setup
   • README.md - Update testing section if test commands changed
```

### Configuration Files Changed

**Files**: `tsconfig.json`, `jest.config.js`, `.eslintrc*`, `pytest.ini`, `Cargo.toml`

**Suggest**:
```
💡 Configuration file modified. Consider updating:
   • CONTRIBUTING.md - Update setup instructions if configuration requirements changed
   • README.md - Update prerequisites if tool versions changed
```

### README or Documentation Modified

**Files**: `README.md`, `CONTRIBUTING.md`, `*.md` in `docs/`

**No suggestion needed** - documentation is already being updated

## How to Present Suggestions

1. **Be concise**: One-line suggestion per file
2. **Be specific**: Mention exact sections that might need updates
3. **Be helpful**: Explain why the update might be needed
4. **Don't be pushy**: Use "Consider updating" or "You may want to update"
5. **Group related suggestions**: Use bullet points under a single message

## Example Outputs

### Example 1: Dependencies Changed
```
💡 package.json modified. Consider updating:
   • README.md - Verify installation instructions reflect new dependencies
   • CHANGELOG.md - If version changed, document the changes
```

### Example 2: New Feature Added
```
💡 New TypeScript file created (src/auth/login.ts). Consider updating:
   • README.md - Document the new authentication feature
   • README.md - Add authentication to the Features section
```

### Example 3: Multiple Changes
If multiple patterns match (e.g., package.json and new source file), combine into one message:
```
💡 Significant changes detected. Consider updating documentation:
   • README.md - Verify installation instructions (dependencies changed)
   • README.md - Document new functionality (new source files added)
   • CHANGELOG.md - Document version changes if applicable
```

## When NOT to Suggest

- Hook is disabled in config (`hooks.doc_updates.enabled: false`)
- File is already a documentation file (*.md)
- File is in node_modules, vendor, or other dependency directories
- File is a generated file (*.min.js, *.bundle.js)
- Tool was used on a file that doesn't typically require doc updates

## Configuration Check

**Before any suggestion**, check:

```
1. Does .claude/readme-and-co.local.md exist?
   - Yes: Read it and check hooks.doc_updates.enabled
     - If false: STOP, do not suggest anything
     - If true or undefined: Continue with suggestions
   - No: Continue with suggestions (enabled by default)
```
