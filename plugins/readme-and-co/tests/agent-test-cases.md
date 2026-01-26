# Agent Testing Guide

This document provides comprehensive test cases for the readme-and-co plugin's doc-generator agent and related functionality.

## Table of Contents

1. [Basic README Generation](#test-case-1-basic-readme-generation)
2. [License Generation](#test-case-2-license-generation)
3. [Configuration Support](#test-case-3-local-configuration)
4. [Badge Generation](#test-case-4-badge-auto-generation)
5. [Monorepo Support](#test-case-5-monorepo-documentation)
6. [Preview Mode](#test-case-6-preview-mode)
7. [Template Validation](#test-case-7-template-validation)
8. [Documentation Updates Hook](#test-case-8-documentation-update-hook)

---

## Test Case 1: Basic README Generation

**Objective**: Generate a minimal README for a new Python project

### Setup

```bash
mkdir test-python-project && cd test-python-project
echo '{"name": "my-app", "version": "1.0.0"}' > package.json
cat > main.py << 'EOF'
def main():
    print("Hello World")

if __name__ == "__main__":
    main()
EOF
```

### Test Steps

1. **Detect project info**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py --pretty
   ```

2. **Generate README**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars '{"project_name":"my-app","description":"A simple Python app","installation_command":"pip install -e .","language":"python","usage_example":"from my_app import main\nmain()","license":"MIT"}' \
     --output README.md
   ```

### Expected Results

- ✅ `README.md` created
- ✅ Contains project name "my-app"
- ✅ Includes installation instructions
- ✅ Has usage example in Python
- ✅ License section present

### Verification

```bash
test -f README.md && echo "✅ README exists"
grep "my-app" README.md && echo "✅ Project name found"
grep "pip install" README.md && echo "✅ Installation command found"
grep "MIT" README.md && echo "✅ License mentioned"
```

---

## Test Case 2: License Generation

**Objective**: Generate multiple license types with auto-detection

### Setup

```bash
mkdir test-licenses && cd test-licenses
git init
git config user.name "Test User"
git config user.email "test@example.com"
```

### Test Steps

1. **MIT License with auto-detection**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/populate_license.py \
     --license MIT \
     --auto-detect \
     --output LICENSE
   ```

2. **Apache 2.0 License with manual info**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/populate_license.py \
     --license Apache-2.0 \
     --holder "My Company" \
     --year 2024 \
     --output LICENSE-APACHE
   ```

3. **Preview without writing**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/populate_license.py \
     --license MIT \
     --holder "Preview Test" \
     --year 2024 \
     --preview
   ```

### Expected Results

- ✅ MIT LICENSE file created with git user info
- ✅ Apache LICENSE file created with "My Company"
- ✅ Preview outputs to stdout, no file created
- ✅ Copyright year is correct

### Verification

```bash
test -f LICENSE && echo "✅ MIT LICENSE exists"
grep "Test User" LICENSE && echo "✅ Auto-detected user name"
test -f LICENSE-APACHE && echo "✅ Apache LICENSE exists"
grep "My Company" LICENSE-APACHE && echo "✅ Manual holder found"
```

---

## Test Case 3: Local Configuration

**Objective**: Use local config for project defaults

### Setup

```bash
mkdir test-config && cd test-config
mkdir -p .claude
cat > .claude/readme-and-co.local.md << 'EOF'
---
defaults:
  project_name: ConfiguredProject
  description: Project configured via local file
  author_name: Config Author
  license: Apache-2.0
badges:
  enabled: true
  style: flat-square
  include:
    - license
    - language-version
---
# Local Config
EOF
```

### Test Steps

1. **Render README using config**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars '{"installation_command":"npm install","language":"javascript","usage_example":"import thing from \u0027thing\u0027"}' \
     --output README.md
   ```

2. **Override config with CLI**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars '{"project_name":"OverriddenName","description":"CLI override","installation_command":"npm install","language":"javascript","usage_example":"test","license":"MIT"}' \
     --preview
   ```

### Expected Results

- ✅ README uses "ConfiguredProject" from config
- ✅ Description from config applied
- ✅ CLI override uses "OverriddenName" instead
- ✅ Config loading message appears in stderr

### Verification

```bash
grep "ConfiguredProject" README.md && echo "✅ Config project name used"
grep "Project configured via local file" README.md && echo "✅ Config description used"
grep "Apache-2.0" README.md && echo "✅ Config license used"
```

---

## Test Case 4: Badge Auto-Generation

**Objective**: Generate shields.io badges based on project detection

### Setup

```bash
mkdir test-badges && cd test-badges
git init
gh repo create test-badges --public --confirm
mkdir -p .claude .github/workflows
cat > .claude/readme-and-co.local.md << 'EOF'
---
defaults:
  license: MIT
badges:
  enabled: true
  style: flat-square
  include:
    - license
    - ci-status
    - language-version
---
EOF
cat > package.json << 'EOF'
{"name": "test-badges", "version": "1.0.0"}
EOF
cat > .github/workflows/ci.yml << 'EOF'
name: CI
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
EOF
```

### Test Steps

1. **Detect project with badges**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py --pretty
   ```

2. **Generate README with badges**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py > project-info.json
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars "$(cat project-info.json)" \
     --preview
   ```

### Expected Results

- ✅ Project info includes "badges" field
- ✅ Badges include license badge
- ✅ Badges include CI status badge (GitHub Actions detected)
- ✅ Badges include language version badge
- ✅ All badges use flat-square style

### Verification

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py | jq '.badges' && echo "✅ Badges generated"
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py | grep "shields.io" && echo "✅ Shields.io badges present"
```

---

## Test Case 5: Monorepo Documentation

**Objective**: Generate documentation for a monorepo structure

### Setup

```bash
mkdir test-monorepo && cd test-monorepo
mkdir -p packages/{core,utils,api}
cat > pnpm-workspace.yaml << 'EOF'
packages:
  - 'packages/*'
EOF
echo '{"name": "@myorg/core"}' > packages/core/package.json
echo '{"name": "@myorg/utils"}' > packages/utils/package.json
echo '{"name": "@myorg/api"}' > packages/api/package.json
```

### Test Steps

1. **Detect monorepo structure**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py --pretty
   ```

2. **Generate root README**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/monorepo/ROOT.template.md \
     --vars '{"project_name":"MyMonorepo","description":"A monorepo project","badges":"","monorepo_type":"pnpm-workspaces","package_count":"3","package_table":"| Package | Description |\n|---------|-------------|\n| @myorg/core | Core package |\n| @myorg/utils | Utilities |\n| @myorg/api | API layer |","prerequisites":"Node.js 18+, pnpm","install_command":"pnpm install","build_command":"pnpm build","dev_command":"pnpm dev","package_command_example":"pnpm --filter @myorg/core dev","add_dependency_example":"pnpm --filter @myorg/core add lodash","new_package_instructions":"Copy existing package structure","test_command":"pnpm test","test_package_command":"pnpm --filter @myorg/core test","workspace_scripts":"build, test, dev, lint, clean","package_descriptions":"See individual package READMEs","license":"MIT"}' \
     --output README.md
   ```

3. **Generate package README**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/monorepo/PACKAGE.template.md \
     --vars '{"package_name":"core","badges":"","project_name":"MyMonorepo","root_readme_path":"../../README.md","description":"Core functionality","install_command":"pnpm install","external_install_command":"npm install @myorg/core","usage_description":"Import and use core functions","language":"typescript","usage_example":"import { fn } from \u0027@myorg/core\u0027;","api_documentation":"See API.md","workspace_install_command":"pnpm install","build_this_package_command":"pnpm --filter @myorg/core build","dev_command":"pnpm --filter @myorg/core dev","test_command":"pnpm --filter @myorg/core test","test_watch_command":"pnpm --filter @myorg/core test --watch","build_command":"pnpm --filter @myorg/core build","internal_dependencies":"@myorg/utils","external_dependencies":"lodash","related_packages":"@myorg/utils, @myorg/api","contributing_path":"../../CONTRIBUTING.md","license":"MIT","license_path":"../../LICENSE"}' \
     --output packages/core/README.md
   ```

### Expected Results

- ✅ Monorepo detected correctly
- ✅ Package count is 3
- ✅ Packages list includes all three packages
- ✅ Root README includes package table
- ✅ Package README links to root
- ✅ Workspace commands are pnpm-specific

### Verification

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py | jq '.monorepo.package_count' | grep 3 && echo "✅ Detected 3 packages"
grep "pnpm-workspaces" README.md && echo "✅ Monorepo type mentioned"
test -f packages/core/README.md && echo "✅ Package README generated"
grep "MyMonorepo" packages/core/README.md && echo "✅ Package links to root"
```

---

## Test Case 6: Preview Mode

**Objective**: Test preview mode for all scripts

### Test Steps

1. **Preview README rendering**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars '{"project_name":"PreviewTest","description":"Testing preview","installation_command":"npm install","language":"javascript","usage_example":"test()","license":"MIT"}' \
     --preview
   ```

2. **Preview license generation**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/populate_license.py \
     --license MIT \
     --holder "Preview User" \
     --year 2024 \
     --preview
   ```

### Expected Results

- ✅ Both commands output to stdout
- ✅ "Preview mode: output to stdout" message in stderr
- ✅ No files created
- ✅ Content is properly formatted

### Verification

```bash
# Should output content, not create file
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md --vars '{"project_name":"Test","description":"Test","installation_command":"npm i","language":"js","usage_example":"x","license":"MIT"}' --preview | grep "# Test" && echo "✅ Preview outputs content"
```

---

## Test Case 7: Template Validation

**Objective**: Validate templates before rendering

### Test Steps

1. **Validate template with all variables**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars '{"project_name":"Test","description":"Test","installation_command":"npm install","language":"javascript","usage_example":"console.log()","license":"MIT"}' \
     --validate
   ```

2. **Validate template with missing variables**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-MINIMAL.template.md \
     --vars '{"project_name":"Test"}' \
     --validate
   ```

3. **Validate all templates**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_templates.py
   ```

### Expected Results

- ✅ Complete validation passes with no errors
- ✅ Missing variables validation shows errors
- ✅ Template validator identifies all templates
- ✅ Validation messages are clear

### Verification

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_templates.py && echo "✅ All templates valid"
```

---

## Test Case 8: Documentation Update Hook

**Objective**: Test documentation update suggestions hook

### Setup

```bash
mkdir test-hooks && cd test-hooks
```

### Test Steps

1. **Verify hook exists**:
   ```bash
   test -f ${CLAUDE_PLUGIN_ROOT}/hooks/PostToolUse/doc-update-check.md && echo "✅ Hook file exists"
   ```

2. **Check hook frontmatter**:
   ```bash
   head -7 ${CLAUDE_PLUGIN_ROOT}/hooks/PostToolUse/doc-update-check.md | grep "event: PostToolUse" && echo "✅ Hook configured for PostToolUse"
   ```

3. **Test with config disabled**:
   ```bash
   mkdir -p .claude
   cat > .claude/readme-and-co.local.md << 'EOF'
---
hooks:
  doc_updates:
    enabled: false
---
EOF
   # Hook should not trigger suggestions when disabled
   ```

4. **Test with config enabled**:
   ```bash
   cat > .claude/readme-and-co.local.md << 'EOF'
---
hooks:
  doc_updates:
    enabled: true
---
EOF
   # Hook should trigger suggestions when files are modified
   ```

### Expected Results

- ✅ Hook file has correct frontmatter
- ✅ Hook respects enabled/disabled config
- ✅ Hook triggers on Write/Edit of relevant files
- ✅ Suggestions are helpful and context-specific

### Verification

```bash
grep "name: doc-update-check" ${CLAUDE_PLUGIN_ROOT}/hooks/PostToolUse/doc-update-check.md && echo "✅ Hook name correct"
grep "tools:" ${CLAUDE_PLUGIN_ROOT}/hooks/PostToolUse/doc-update-check.md && echo "✅ Tools specified"
```

---

## Integration Test: Complete Workflow

**Objective**: Test entire documentation generation workflow

### Setup

```bash
mkdir complete-test && cd complete-test
git init
gh repo create complete-test --public --confirm
echo '{"name": "complete-test", "version": "1.0.0", "dependencies": {"express": "^4.18.0"}}' > package.json
cat > index.js << 'EOF'
const express = require('express');
const app = express();
app.listen(3000);
EOF
mkdir -p .claude
cat > .claude/readme-and-co.local.md << 'EOF'
---
defaults:
  author_name: Integration Test
  license: MIT
badges:
  enabled: true
  style: flat-square
---
EOF
```

### Complete Workflow

1. **Detect project**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/detect_project_info.py > project-info.json
   ```

2. **Generate README**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_template.py \
     --template ${CLAUDE_PLUGIN_ROOT}/templates/README/full/README-STANDARD.template.md \
     --vars "$(cat project-info.json)" \
     --output README.md
   ```

3. **Generate LICENSE**:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/populate_license.py \
     --license MIT \
     --auto-detect \
     --output LICENSE
   ```

4. **Validate results**:
   ```bash
   test -f README.md && test -f LICENSE && echo "✅ Complete workflow succeeded"
   ```

### Expected Results

- ✅ Project detected correctly (JavaScript)
- ✅ README generated with badges
- ✅ LICENSE generated with auto-detected info
- ✅ All files valid and properly formatted
- ✅ Config defaults applied

---

## Running All Tests

Create a test runner script:

```bash
cat > run-all-tests.sh << 'EOF'
#!/bin/bash

echo "Running readme-and-co agent tests..."
echo "===================================="

# Test 1
echo "Test 1: Basic README Generation"
# Add test commands

# Test 2
echo "Test 2: License Generation"
# Add test commands

# Add all other tests...

echo "===================================="
echo "All tests completed"
EOF

chmod +x run-all-tests.sh
./run-all-tests.sh
```

## Best Practices for Agent Testing

1. **Clean environment**: Start each test in a fresh directory
2. **Verify outputs**: Check both file existence and content
3. **Test edge cases**: Missing files, invalid input, etc.
4. **Use preview mode**: For non-destructive testing
5. **Test config integration**: Verify config loading and priority
6. **Document failures**: Note any unexpected behavior
7. **Cleanup**: Remove test directories after completion
