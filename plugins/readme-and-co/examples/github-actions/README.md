# GitHub Actions Workflows for readme-and-co

This directory contains example GitHub Actions workflows for automating documentation maintenance.

## Available Workflows

### 1. Auto-Update Documentation (`auto-update-docs.yml`)

Automatically regenerates documentation when project files change and creates a pull request.

**Triggers on**:
- Changes to `package.json`, `pyproject.toml`, `Cargo.toml`, `requirements.txt`, or `Gemfile`
- Pushes to `main` branch

**What it does**:
1. Detects current project information
2. Regenerates README from template
3. Creates a PR if changes are detected

**Setup**:
```bash
mkdir -p .github/workflows
cp examples/github-actions/auto-update-docs.yml .github/workflows/
```

**Customization**:
- Change `branches` to match your main branch name
- Adjust `paths` to include additional files that should trigger updates
- Modify the template path if using a different README template
- Customize PR title, body, and labels

---

### 2. Validate Documentation (`validate-docs.yml`)

Validates documentation quality on pull requests.

**Triggers on**:
- Pull requests modifying markdown, templates, or scripts

**What it does**:
1. Validates template syntax
2. Checks for broken links
3. Lints markdown files
4. Tests template rendering
5. Verifies README freshness

**Setup**:
```bash
mkdir -p .github/workflows
cp examples/github-actions/validate-docs.yml .github/workflows/
```

**Required configuration files**:

Create `.github/markdown-link-check-config.json`:
```json
{
  "ignorePatterns": [
    {
      "pattern": "^http://localhost"
    }
  ],
  "timeout": "20s",
  "retryOn429": true,
  "retryCount": 3,
  "fallbackRetryDelay": "30s"
}
```

Create `.cspell.json` (optional):
```json
{
  "version": "0.2",
  "language": "en",
  "words": [],
  "ignoreWords": [],
  "ignorePaths": [
    "node_modules",
    "dist",
    "build"
  ]
}
```

**Customization**:
- Disable spell checking by removing the `Check spelling` step
- Adjust markdown linting rules via `.markdownlint.json`
- Modify link check patterns to match your needs

---

## Installation Guide

### Quick Setup (Both Workflows)

```bash
# Create workflows directory
mkdir -p .github/workflows

# Copy both workflows
cp examples/github-actions/auto-update-docs.yml .github/workflows/
cp examples/github-actions/validate-docs.yml .github/workflows/

# Create link check config
mkdir -p .github
cat > .github/markdown-link-check-config.json << 'EOF'
{
  "ignorePatterns": [
    {"pattern": "^http://localhost"}
  ],
  "timeout": "20s"
}
EOF

# Commit
git add .github/
git commit -m "ci: add documentation automation workflows"
git push
```

### Permissions

The workflows require these permissions (set in workflow file):

**auto-update-docs.yml**:
- `contents: write` - To commit changes
- `pull-requests: write` - To create PRs

**validate-docs.yml**:
- `contents: read` - To read repository files (default)

## Usage Examples

### Scenario 1: Dependency Added

1. Developer adds a new dependency to `package.json`
2. Commits and pushes to `main`
3. `auto-update-docs.yml` triggers
4. Workflow regenerates README with new dependency information
5. Creates PR: "docs: Update README based on project changes"
6. Team reviews and merges PR

### Scenario 2: Documentation PR

1. Developer updates README.md
2. Creates PR
3. `validate-docs.yml` triggers
4. Workflow validates:
   - Template syntax
   - Broken links
   - Markdown formatting
   - Spelling
5. PR shows validation results
6. Developer fixes any issues before merge

### Scenario 3: Template Changes

1. Developer updates a README template
2. Creates PR
3. `validate-docs.yml` triggers
4. Tests template rendering with sample data
5. Ensures templates work correctly before merge

## Customization Options

### Change Trigger Files

Edit `auto-update-docs.yml`:

```yaml
paths:
  - 'package.json'
  - 'pyproject.toml'
  - 'your-config.yml'  # Add custom files
```

### Use Different Template

Edit `auto-update-docs.yml`:

```yaml
- name: Regenerate README
  run: |
    python3 scripts/render_template.py \
      --template templates/README/full/README-COMPREHENSIVE.template.md \  # Change template
      --vars "$(cat project-info.json)" \
      --output README.md
```

### Customize PR

Edit `auto-update-docs.yml`:

```yaml
- name: Create Pull Request
  uses: peter-evans/create-pull-request@v6
  with:
    title: 'chore: update documentation'  # Custom title
    labels: |
      documentation
      automated
      high-priority  # Add labels
    reviewers: |
      username1
      username2  # Auto-assign reviewers
```

### Add Slack Notifications

Add to end of `auto-update-docs.yml`:

```yaml
- name: Notify on Slack
  if: steps.changes.outputs.changed == 'true'
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Documentation update PR created",
        "blocks": [
          {
            "type": "section",
            "text": {
              "type": "mrkdwn",
              "text": "README auto-update PR created: ${{ github.server_url }}/${{ github.repository }}/pull/${{ steps.create-pr.outputs.pull-request-number }}"
            }
          }
        ]
      }
```

### Schedule Regular Checks

Add to `validate-docs.yml`:

```yaml
on:
  pull_request:
    paths:
      - '**.md'
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday at midnight
  workflow_dispatch:  # Manual trigger
```

## Troubleshooting

### Workflow Not Triggering

**Check**:
1. Workflow file is in `.github/workflows/`
2. File has `.yml` or `.yaml` extension
3. Paths match changed files
4. Branch name matches trigger configuration

**Debug**:
```bash
# Validate workflow syntax
cat .github/workflows/auto-update-docs.yml | docker run --rm -i rhysd/actionlint:latest -
```

### Permission Denied

**Fix**: Add permissions to workflow file:

```yaml
permissions:
  contents: write
  pull-requests: write
```

### Script Not Found

**Fix**: Ensure paths are relative to repository root:

```yaml
run: |
  python3 scripts/detect_project_info.py  # Not ./scripts/...
```

### Python Dependencies Missing

**Fix**: Install requirements if needed:

```yaml
- name: Install dependencies
  run: |
    pip install -r requirements.txt  # If you have any
```

## Advanced Usage

### Monorepo Support

For monorepos, detect and update multiple READMEs:

```yaml
- name: Update package READMEs
  run: |
    for pkg in packages/*/; do
      cd "$pkg"
      python3 ../../scripts/render_template.py \
        --template ../../templates/README/monorepo/PACKAGE.template.md \
        --vars package-vars.json \
        --output README.md
      cd -
    done
```

### Multi-Language Projects

Detect primary language and use appropriate template:

```yaml
- name: Detect and use appropriate template
  run: |
    LANG=$(python3 scripts/detect_project_info.py | jq -r '.primary_language')
    case "$LANG" in
      python)
        TEMPLATE="templates/README/full/README-PYTHON.template.md"
        ;;
      javascript)
        TEMPLATE="templates/README/full/README-JAVASCRIPT.template.md"
        ;;
      *)
        TEMPLATE="templates/README/full/README-STANDARD.template.md"
        ;;
    esac
    python3 scripts/render_template.py --template "$TEMPLATE" ...
```

## Best Practices

1. **Review auto-generated PRs** - Don't auto-merge, always review
2. **Keep templates updated** - Regularly review and improve templates
3. **Test locally first** - Run scripts locally before pushing
4. **Use preview mode** - Test with `--preview` flag during development
5. **Version control workflows** - Keep workflows in version control
6. **Monitor workflow runs** - Check Actions tab for failures
7. **Document customizations** - Comment your changes in workflow files

## See Also

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [readme-and-co Plugin Documentation](../../README.md)
