# Hook Configuration Examples

## Enabling/Disabling the Documentation Update Hook

The doc-update-check hook can be controlled via `.claude/readme-and-co.local.md`.

### Enabled (Default)

If no config exists, or if the hook is explicitly enabled:

```yaml
---
hooks:
  doc_updates:
    enabled: true
---
```

The hook will provide suggestions after Write/Edit operations.

### Disabled

To disable the hook:

```yaml
---
hooks:
  doc_updates:
    enabled: false
---
```

The hook will not provide any suggestions.

## Use Cases

### Enable During Active Development

```yaml
---
defaults:
  project_name: my-app
  license: MIT
hooks:
  doc_updates:
    enabled: true
---
```

Helpful reminders to keep documentation in sync.

### Disable During Bulk Refactoring

```yaml
---
hooks:
  doc_updates:
    enabled: false
---
```

Prevent noise during large-scale changes. Re-enable when done.

### Disable Permanently for Auto-Generated Projects

```yaml
---
hooks:
  doc_updates:
    enabled: false
---
```

For projects where documentation is auto-generated.

## Hook Trigger Patterns

The hook checks file paths after Write/Edit and suggests updates for:

| File Pattern | Suggestion |
|-------------|------------|
| `package.json`, `pyproject.toml`, `Cargo.toml` | README installation, CHANGELOG version |
| New `*.ts`, `*.py`, `*.rs` files (Write only) | README usage, features |
| `.github/workflows/*`, `.gitlab-ci.yml` | CONTRIBUTING CI/CD, README badges |
| `test_*.py`, `*.test.ts`, `*.spec.js` | CONTRIBUTING testing, README testing |
| `tsconfig.json`, `jest.config.js` | CONTRIBUTING setup, README prerequisites |

## Integration with Other Config

Hooks work alongside other config options:

```yaml
---
# Project defaults
defaults:
  project_name: awesome-app
  license: MIT
  author_name: Developer Name

# Badge settings
badges:
  enabled: true
  style: flat-square

# Hook settings
hooks:
  doc_updates:
    enabled: true
---
```

All settings in one file for easy management.
