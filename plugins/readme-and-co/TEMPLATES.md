# Template Library Reference

Complete reference for all templates in the readme-and-co plugin.

## Quick Start

Templates are rendered using the `render_template.py` script with variable substitution:

```bash
python scripts/render_template.py \
  --template templates/README/full/README-STANDARD.template.md \
  --vars '{"project_name":"my-app","description":"A cool tool"}' \
  --output README.md
```

## Global Variables

These variables are available in all templates and are automatically detected or have smart defaults:

- `project_name`: string - Repository/project name (from package.json, git remote, or directory name)
- `description`: string - One-line project description
- `author_name`: string - Project author (from git config user.name or package.json)
- `author_email`: string - Contact email (from git config user.email)
- `year`: number - Current year for copyright (auto-detected)
- `repo_url`: string - GitHub repository URL (from git remote)
- `license`: string - License type (e.g., "MIT", "Apache-2.0")

## README Templates

### README-MINIMAL.template.md

**Location**: `templates/README/full/README-MINIMAL.template.md`

Minimal README with essential sections only.

**When to use**: Small projects, scripts, personal tools, quick prototypes

**Variables**:
- All global variables
- `installation_command`: string - Installation command (e.g., "npm install my-package")
- `language`: string - Language for code blocks (e.g., "bash", "python", "javascript")
- `usage_example`: string - Simple usage example code

**Example**:
```bash
python scripts/render_template.py \
  --template templates/README/full/README-MINIMAL.template.md \
  --vars '{
    "project_name": "my-cli-tool",
    "description": "A simple CLI utility",
    "installation_command": "npm install -g my-cli-tool",
    "language": "bash",
    "usage_example": "my-cli-tool --help",
    "license": "MIT"
  }' \
  --output README.md
```

### README-STANDARD.template.md

**Location**: `templates/README/full/README-STANDARD.template.md`

Standard README with common sections for most open source projects.

**When to use**: Most projects, libraries, applications (recommended default)

**Variables**:
- All global variables
- `features`: string - Bulleted list of key features
- `prerequisites`: string - Required software/dependencies
- `installation_command`: string - Installation instructions
- `usage_description`: string - Description of how to use
- `language`: string - Language for code blocks
- `usage_example`: string - Usage code example

**Example**:
```bash
python scripts/render_template.py \
  --template templates/README/full/README-STANDARD.template.md \
  --vars '{
    "project_name": "fastapi-boilerplate",
    "description": "Production-ready FastAPI boilerplate",
    "features": "- Fast API development\\n- Built-in authentication\\n- Docker support",
    "prerequisites": "- Python 3.11+\\n- PostgreSQL 14+",
    "installation_command": "pip install -r requirements.txt",
    "usage_description": "Start the development server:",
    "language": "bash",
    "usage_example": "uvicorn app.main:app --reload",
    "license": "MIT"
  }' \
  --output README.md
```

### README-COMPREHENSIVE.template.md

**Location**: `templates/README/full/README-COMPREHENSIVE.template.md`

Comprehensive README with all possible sections including API docs, deployment, architecture, performance, security, troubleshooting, and more.

**When to use**: Large projects, frameworks, libraries with extensive APIs

**Key variables** (49 total):
- All variables from STANDARD template
- `api_overview`, `api_methods` - API documentation
- `architecture_description`, `component_diagram`, `data_flow_description` - Architecture details
- `deployment_instructions`, `docker_commands` - Deployment guides
- `performance_description`, `benchmark_results`, `optimization_tips` - Performance info
- `security_overview` - Security documentation
- `common_issues`, `faq_content` - Troubleshooting and FAQ
- `upcoming_features` - Roadmap
- Plus many more for comprehensive documentation

**Example**:
```bash
python scripts/render_template.py \
  --template templates/README/full/README-COMPREHENSIVE.template.md \
  --vars '{
    "project_name": "my-framework",
    "description": "A comprehensive framework for...",
    "badges": "...",
    "features": "- Feature 1\n- Feature 2",
    "prerequisites": "- Node.js 18+\n- Docker",
    "installation_command": "npm install my-framework",
    "usage_description": "Quick start guide",
    "usage_example": "import { Framework } from \"my-framework\"",
    "api_overview": "Complete API reference...",
    "architecture_description": "System architecture overview...",
    "deployment_instructions": "Deployment steps...",
    "license": "MIT"
  }' \
  --output README.md
```

## SECURITY Templates

### SECURITY-BASIC.template.md

**Location**: `templates/SECURITY/full/SECURITY-BASIC.template.md`

Basic security policy with email contact.

**When to use**: Small to medium projects, standard security reporting

**Variables**:
- `project_name`: string
- `security_email`: string - Email for security reports
- `current_version`: string - Current supported version

**Example**:
```bash
python scripts/render_template.py \
  --template templates/SECURITY/full/SECURITY-BASIC.template.md \
  --vars '{
    "project_name": "my-app",
    "security_email": "security@example.com",
    "current_version": "1.0.x"
  }' \
  --output SECURITY.md
```

### SECURITY-ENTERPRISE.template.md

**Location**: `templates/SECURITY/full/SECURITY-ENTERPRISE.template.md`

Enterprise-grade security policy with comprehensive security program details including bug bounty, security team, SLAs, compliance standards, security architecture, and audit procedures.

**When to use**: Large/commercial projects, projects with security teams, enterprises with compliance requirements

**Key variables** (44 total):
- All variables from BASIC template
- `policy_version`, `last_updated` - Policy metadata
- `ciso_email`, `ciso_pgp`, `security_lead_email`, `security_lead_pgp` - Security team contacts
- `emergency_contact`, `security_mailing_list` - Communication channels
- `vulnerability_reporting_platform` - Reporting platform URL
- `bug_bounty_description`, `min_bounty`, `max_bounty` - Bug bounty program
- `compliance_standards`, `certifications`, `security_frameworks` - Compliance info
- `auth_method`, `authz_method`, `encryption_standards` - Security architecture
- `static_analysis_tools`, `dynamic_analysis_tools`, `dependency_scan_tools` - Security tooling
- `pentest_frequency`, `audit_frequency` - Audit schedules
- Plus many more for comprehensive security documentation

**Example**:
```bash
python scripts/render_template.py \
  --template templates/SECURITY/full/SECURITY-ENTERPRISE.template.md \
  --vars '{
    "project_name": "enterprise-app",
    "policy_version": "2.0",
    "last_updated": "2026-01-31",
    "security_email": "security@company.com",
    "ciso_email": "ciso@company.com",
    "vulnerability_reporting_platform": "https://bugcrowd.com/company",
    "bug_bounty_description": "We offer rewards from $100 to $10,000",
    "min_bounty": "$100",
    "max_bounty": "$10,000",
    "compliance_standards": "SOC 2 Type II, ISO 27001, GDPR",
    "current_version": "2.x",
    "minimum_supported_version": "2.0"
  }' \
  --output SECURITY.md
```

## CONTRIBUTING Templates

### CONTRIBUTING-BASIC.template.md

**Location**: `templates/CONTRIBUTING/full/CONTRIBUTING-BASIC.template.md`

Basic contribution guide with setup and PR process.

**When to use**: Small projects, clear contribution process

**Variables**:
- `project_name`: string
- `setup_commands`: string - Development setup commands
- `code_style_guidelines`: string - Code style description or link

**Example**:
```bash
python scripts/render_template.py \
  --template templates/CONTRIBUTING/full/CONTRIBUTING-BASIC.template.md \
  --vars '{
    "project_name": "my-lib",
    "setup_commands": "npm install\\nnpm run dev",
    "code_style_guidelines": "Follow the ESLint rules in .eslintrc.json"
  }' \
  --output CONTRIBUTING.md
```

### CONTRIBUTING-DETAILED.template.md

**Location**: `templates/CONTRIBUTING/full/CONTRIBUTING-DETAILED.template.md` (to be created)

Detailed guide with testing, commit conventions, release process.

**When to use**: Projects with many contributors, strict processes

**Additional variables**: testing_requirements, commit_conventions, release_process

## LICENSE Templates

All license templates are located in `templates/LICENSE/` with subdirectories:

- `github/` - 13 GitHub-approved licenses
- `creative-commons/` - 7 Creative Commons licenses
- `fsl/` - FSL-1.1-MIT
- `multi-license/` - Multi-licensing templates

Use `populate_license.py` script for licenses:

```bash
python scripts/populate_license.py \
  --license MIT \
  --holder "Jane Doe" \
  --year 2026 \
  --output LICENSE
```

See [LICENSES.md](LICENSES.md) for complete license guidance.

## Issue Templates

### bug_report.yml.template

**Location**: `templates/ISSUE_TEMPLATES/full/bug_report.yml.template`

YAML issue template for bug reports.

**When to use**: All projects (recommended over Markdown format)

**Variables**:
- `environment_specific_fields`: string - Project-specific environment fields

**Example**:
```bash
python scripts/render_template.py \
  --template templates/ISSUE_TEMPLATES/full/bug_report.yml.template \
  --vars '{
    "environment_specific_fields": "- Browser: [e.g., Chrome 120]\\n- Node version: [e.g., 18.17.0]"
  }' \
  --output .github/ISSUE_TEMPLATE/bug_report.yml
```

### feature_request.yml.template

**Location**: `templates/ISSUE_TEMPLATES/full/feature_request.yml.template`

YAML issue template for feature requests.

**When to use**: All projects

**Variables**: None (static template)

## Pull Request Templates

### PULL_REQUEST_TEMPLATE.md.template

**Location**: `templates/PR_TEMPLATES/full/PULL_REQUEST_TEMPLATE.md.template`

Standard PR template with checklist.

**When to use**: Most projects

**Variables**: None (static template)

**Example**:
```bash
python scripts/render_template.py \
  --template templates/PR_TEMPLATES/full/PULL_REQUEST_TEMPLATE.md.template \
  --vars '{}' \
  --output .github/pull_request_template.md
```

## Template Rendering

### Variable Substitution

Templates use `{{variable_name}}` syntax:

```markdown
# {{project_name}}

{{description}}

Author: {{author_name}}
```

### Missing Variables

If a variable is not provided, the renderer:
1. Shows a warning in stderr
2. Uses placeholder: `[MISSING: variable_name]`

Example:
```
Warning: Missing variable: author_email
```

Output: `Contact: [MISSING: author_email]`

### Default Values

The `populate_license.py` script provides smart defaults:
- `year` - Current year
- `author_name` - From git config user.name
- `author_email` - From git config user.email
- `copyright_holder` - Same as author_name

For other templates, provide all required variables or they will show `[MISSING: ...]`.

## Template Creation Guide

### Full Templates

Full templates should:
- Be complete, standalone documents
- Use `{{variable}}` for all customizable parts
- Include all required sections for the document type
- Have `.template.md` or `.template.txt` extension

## Validation Rules

All templates must:
- Use valid markdown syntax
- Have consistent variable naming (`snake_case`)
- Include example values in TEMPLATES.md documentation
- Be tested with render_template.py
- Not include sensitive information (emails, API keys)

## Creating Custom Templates

To add a new template:

1. Create template file in appropriate directory
2. Use `{{variable}}` syntax for customization points
3. Add documentation to TEMPLATES.md with:
   - Location
   - When to use
   - Variables (with types and descriptions)
   - Complete example
4. Test rendering:
   ```bash
   python scripts/render_template.py \
     --template path/to/template.md \
     --vars '{"var1":"value1"}' \
     --output test-output.md
   ```

## Template Naming Conventions

- Full templates: `DOCUMENT-TYPE-VARIANT.template.ext`
  - Examples: `README-MINIMAL.template.md`, `SECURITY-BASIC.template.md`
- Extensions: `.template.md` for Markdown, `.template.txt` for plain text, `.template.yml` for YAML

## Additional Resources

- See [LICENSES.md](LICENSES.md) for license selection guide
- See skill documentation for best practices:
  - `skills/documentation-standards/SKILL.md`
  - `skills/github-templates/SKILL.md`
- Script documentation:
  - `scripts/render_template.py --help`
  - `scripts/populate_license.py --help`
