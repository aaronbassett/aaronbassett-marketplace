---
name: create
description: Generate comprehensive GitHub repository documentation including README, LICENSE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, and GitHub templates
argument-hint: "[--file FILENAME]"
allowed-tools: ["Task", "AskUserQuestion", "Read", "Glob", "Bash"]
---

# Create Repository Documentation

This command launches an interactive workflow to generate professional GitHub repository documentation following best practices.

## What This Command Does

Launches the `doc-generator` agent to:
1. Analyze your project structure using Explore agents
2. Guide you through an interactive workflow with targeted questions
3. Generate customized documentation files using templates
4. Create or update: README, LICENSE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, SUPPORT, GitHub templates, GOVERNANCE, FUNDING, CODEOWNERS

## Usage Modes

### Interactive Mode (Recommended)

Launch without arguments for full conversational workflow:

```bash
/readme-and-co:create
```

The agent will:
- Detect your project type, languages, frameworks
- Ask what documentation level you need (basic, expanded, comprehensive, custom)
- Guide you through license selection with decision tree
- Help you choose appropriate templates
- Generate all selected files

### Quick File Generation

Create specific files directly:

```bash
/readme-and-co:create --file README.md
/readme-and-co:create --file LICENSE
/readme-and-co:create --file CONTRIBUTING.md
/readme-and-co:create --file .github/ISSUE_TEMPLATE/bug_report.yml
```

The agent will ask minimal questions focused on that specific file.

### Update Mode

When files already exist, the agent offers to update them:

```bash
/readme-and-co:create
# Agent detects existing README.md
# Offers: "Update with missing sections" or "Recreate from scratch"
```

## Command Behavior

### Project Analysis

The agent automatically explores your repository to detect:
- **Languages**: Python, JavaScript, TypeScript, Go, Rust, etc.
- **Package managers**: npm, pip, cargo, go.mod
- **Frameworks**: React, FastAPI, Express, Django, Next.js, etc.
- **Testing**: pytest, jest, cargo test, etc.
- **CI/CD**: GitHub Actions, existing workflows
- **Existing docs**: What documentation already exists

This analysis informs template selection and content customization.

### Documentation Levels

When asked what you need, choose:

**Basic**: Essential files only
- README.md (minimal template)
- LICENSE (guided selection)
- CONTRIBUTING.md (basic)
- SECURITY.md (basic)

**Expanded**: Standard open source project
- All basic files (standard templates)
- CODE_OF_CONDUCT.md
- SUPPORT.md
- Issue templates (bug, feature)
- PR template

**Comprehensive**: Full professional setup
- All expanded files (comprehensive templates)
- GOVERNANCE.md
- FUNDING.yml
- CODEOWNERS
- Multiple issue templates (bug, feature, question, docs)
- Detailed PR template

**Custom**: Select specific files
- Agent presents checklist of all available files
- Choose exactly what you need

### License Selection Process

The agent uses the license-selection skill to guide you through choosing a license:

1. **Detect project type**: Code vs documentation vs mixed
2. **Ask decision tree questions**:
   - "Do you want maximum adoption?" → MIT
   - "Need patent protection?" → Apache-2.0
   - "Want copyleft?" → GPL-3.0/AGPL-3.0
   - "Commercial SaaS?" → FSL-1.1-MIT

3. **Explain options**: Agent provides context about each license
4. **Multi-licensing**: Suggests dual licensing if user is indecisive or project is commercial

For code projects, agent nudges toward GitHub-approved licenses first.
For documentation/media, agent recommends Creative Commons licenses.

### File Output Locations

Files are created in standard GitHub locations:

- `README.md` → Repository root
- `LICENSE` or `LICENSE.md` → Repository root
- `CONTRIBUTING.md` → Repository root
- `SECURITY.md` → Repository root
- `CODE_OF_CONDUCT.md` → Repository root
- `SUPPORT.md` → Repository root
- `GOVERNANCE.md` → Repository root
- `.github/FUNDING.yml` → .github directory
- `CODEOWNERS` → .github/CODEOWNERS or repository root
- `.github/ISSUE_TEMPLATE/*.yml` → .github/ISSUE_TEMPLATE directory
- `.github/PULL_REQUEST_TEMPLATE.md` → .github directory (or PULL_REQUEST_TEMPLATE/ for multiple)

Unless user specifies different locations.

## Template Rendering

The command uses Python scripts for template rendering (context-efficient):

```bash
# Agent never reads templates into context
# Instead calls render_template.py:
# Note: Agent invokes bug-fixes:find-claude-plugin-root skill first
PLUGIN_ROOT=$(python3 /tmp/cpr.py readme-and-co)
python "$PLUGIN_ROOT/scripts/render_template.py" \
  --template templates/README/full/README-STANDARD.template.md \
  --vars '{"project_name":"my-app","description":"..."}' \
  --output README.md
```

This keeps agent context free for conversation and analysis.

## Progress Feedback

Agent provides step-by-step updates:

```
Analyzing your project...
✓ Detected: Python 3.11, FastAPI, pytest
✓ Found existing: README.md (will offer update)

Generating documentation...
✓ Creating LICENSE (MIT)
✓ Creating CONTRIBUTING.md
✓ Creating SECURITY.md
✓ Updating README.md with missing sections
✓ Creating .github/ISSUE_TEMPLATE/bug_report.yml
✓ Creating .github/ISSUE_TEMPLATE/feature_request.yml

Done! Created 5 files, updated 1 file.

Next steps:
- Review and customize LICENSE copyright holder
- Update CONTRIBUTING.md with your specific development setup
- Test issue templates by creating a test issue
```

## Existing File Handling

When documentation files already exist:

**For README, CONTRIBUTING, SUPPORT** (updatable):
- Agent offers: "Update with missing sections" or "Replace entirely"
- Update mode: Adds missing sections while preserving existing content

**For LICENSE, CODE_OF_CONDUCT** (typically not updated):
- Agent warns: "LICENSE already exists. Replace? (not recommended after releases)"

**For templates** (GitHub templates):
- Agent asks: "Add to existing templates" or "Replace all templates"

## Smart Defaults

The agent uses smart defaults from:

- **Git config**: Author name and email for licenses
- **package.json / pyproject.toml**: Project name, description, version
- **Repository URL**: For badges, links, CODEOWNERS
- **Current year**: For copyright notices

User can override any defaults when prompted.

## Examples

### Example 1: New Project Setup

```
User: /readme-and-co:create

Agent: Analyzing your project...
I detected this is a Python project using FastAPI and pytest.

What documentation do you need?
○ Basic files (README, LICENSE, CONTRIBUTING, SECURITY)
○ Expanded (basic + CODE_OF_CONDUCT, templates)
○ Comprehensive (all documentation)
○ Custom (select specific files)

User: Expanded

Agent: Great! For your FastAPI project, I recommend these licenses:
🌟 Recommended for code:
○ MIT (most popular, maximum adoption)
○ Apache-2.0 (includes patent protection)

Which license fits your needs?

User: MIT

Agent: Perfect. Generating documentation...
[Creates all files with FastAPI-specific content]
```

### Example 2: Quick License Addition

```
User: /readme-and-co:create --file LICENSE

Agent: I'll help you create a LICENSE file.

This appears to be a code project. Which license?
○ MIT (recommended - maximum adoption)
○ Apache-2.0 (patent protection)
○ GPL-3.0 (copyleft)
○ FSL-1.1-MIT (commercial now, MIT in 2 years)
○ Other

User: FSL-1.1-MIT

Agent: Excellent choice for commercial SaaS! FSL gives you a 2-year
revenue window, then automatically becomes MIT.

Copyright holder name? (default: John Doe from git config)

User: MyCompany Inc

Agent: Creating LICENSE.md...
✓ Created LICENSE.md with FSL-1.1-MIT
```

### Example 3: Update Existing README

```
User: /readme-and-co:create

Agent: I see you already have README.md. I can:
○ Update it with missing sections (Contributing, Support, License badge)
○ Replace it entirely with a new README
○ Skip it

What would you like?

User: Update with missing sections

Agent: I'll add the missing sections while preserving your existing content.
✓ Added Contributing section
✓ Added Support section
✓ Added license badge
✓ Updated README.md
```

## Tips for Best Results

**Be specific about your project**: Agent generates better templates when it understands your project type

**Review generated files**: Templates provide good starting points but should be customized

**Use update mode**: For existing projects, update mode preserves your customizations

**Test templates**: Create test issues/PRs to verify templates work as expected

**Commit after generation**: Review in git diff before committing

## Technical Details

**Skills used**:
- `documentation-standards`: README, CONTRIBUTING, SUPPORT guidance
- `license-selection`: License decision trees and recommendations
- `github-templates`: Issue/PR templates, CODEOWNERS

**Scripts invoked**:
- `detect_project_info.py`: Analyzes repository
- `render_template.py`: Generates files from templates
- `populate_license.py`: Creates license files

**Tools required**:
- Python 3.7+ (for scripts)
- Git (for project detection)

## When to Use

Use `/readme-and-co:create` when:
- Starting a new repository
- Open-sourcing an internal project
- Adding missing documentation
- Updating documentation to current standards
- Changing licenses
- Setting up GitHub templates

## Automation Note

This command does NOT automate:
- GitHub Actions workflows (use separate workflow plugin)
- Repository settings (topics, description)
- Branch protection rules
- GitHub Pages setup

Focus is on documentation files only.

---

**IMPORTANT IMPLEMENTATION NOTE FOR CLAUDE:**

When this command is invoked, use the Task tool to launch the `doc-generator` agent:

```
Task(
  subagent_type="doc-generator",
  description="Generate repository documentation",
  prompt="User wants to create repository documentation. [Include any --file argument if provided]"
)
```

The agent will handle the entire workflow autonomously.
