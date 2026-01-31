---
# Local configuration for readme-and-co plugin
# Copy this to .claude/readme-and-co.local.md in your project

# Default values for template variables
# These can be overridden by CLI arguments
defaults:
  # Project information
  project_name: MyProject
  description: A short description of the project

  # Author information
  author_name: Your Name
  author_email: you@example.com

  # License
  license: MIT

  # Repository (auto-detected if not specified)
  # repo_url: https://github.com/username/repo

# Badge configuration
badges:
  enabled: true
  style: flat-square  # Options: flat, flat-square, plastic, for-the-badge
  include:
    - license
    - ci-status
    - language-version

# Template preferences
templates:
  readme_variant: standard  # Options: minimal, standard, comprehensive

# Documentation hooks
hooks:
  doc_updates:
    enabled: true
---

# Local Configuration Example

This file shows the available configuration options for the readme-and-co plugin.

## Usage

1. Copy this file to `.claude/readme-and-co.local.md` in your project root
2. Modify the values in the YAML frontmatter (between the `---` markers)
3. The defaults will be used when generating documentation

## Priority

Configuration values have the following priority (highest to lowest):

1. **CLI arguments** - Values passed via `--vars` flag
2. **Local config** - Values in `.claude/readme-and-co.local.md`
3. **Auto-detection** - Values detected from git, package.json, etc.
4. **Defaults** - Built-in default values

## Examples

### Minimal Configuration

```yaml
---
defaults:
  project_name: my-app
  license: Apache-2.0
---
```

### Full Configuration

```yaml
---
defaults:
  project_name: awesome-project
  description: An awesome web application
  author_name: Jane Developer
  author_email: jane@example.com
  license: MIT

badges:
  enabled: true
  style: flat-square
  include:
    - license
    - build-status
    - coverage
    - npm-version

templates:
  readme_variant: comprehensive

hooks:
  doc_updates:
    enabled: true
---
```
