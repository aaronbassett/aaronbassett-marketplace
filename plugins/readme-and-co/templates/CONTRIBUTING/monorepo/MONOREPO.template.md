# Contributing to {{project_name}}

Thank you for your interest in contributing! This guide will help you navigate our {{monorepo_type}} monorepo structure.

## Table of Contents

- [Monorepo Structure](#monorepo-structure)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Working with Packages](#working-with-packages)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)

## Monorepo Structure

This repository contains {{package_count}} packages:

{{package_list}}

### Directory Structure

```
{{project_name}}/
├── packages/          # Shared packages
├── apps/             # Applications
├── libs/             # Utility libraries
└── services/         # Backend services
```

## Getting Started

### Prerequisites

{{prerequisites}}

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone {{repo_url}}
   cd {{project_name}}
   ```

2. **Install dependencies** (for all packages):
   ```bash
   {{install_command}}
   ```

3. **Build all packages**:
   ```bash
   {{build_command}}
   ```

4. **Verify setup**:
   ```bash
   {{test_command}}
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or changes

### 2. Make Changes

Work in the relevant package(s):

```bash
cd packages/your-package
# Make your changes
```

### 3. Run Tests

```bash
# Test specific package
{{test_package_command}}

# Test all packages
{{test_all_command}}
```

### 4. Build

```bash
# Build specific package
{{build_package_command}}

# Build all packages
{{build_all_command}}
```

## Working with Packages

### Running Commands in Specific Packages

{{workspace_command_examples}}

### Adding Dependencies

**To a specific package**:
```bash
{{add_dependency_command}}
```

**To workspace root** (shared dev dependencies):
```bash
{{add_root_dependency_command}}
```

### Creating a New Package

{{new_package_steps}}

### Package Dependencies

When one package depends on another:

{{internal_dependency_setup}}

### Versioning

We use {{versioning_strategy}} for package versioning:

{{versioning_instructions}}

## Testing

### Running Tests

```bash
# All packages
{{test_all_command}}

# Specific package
{{test_package_command}}

# Watch mode
{{test_watch_command}}

# Coverage
{{test_coverage_command}}
```

### Writing Tests

{{test_guidelines}}

## Submitting Changes

### Before Submitting

- [ ] All tests pass
- [ ] Code follows our style guide
- [ ] Documentation is updated
- [ ] Changeset created (if applicable)
- [ ] No lint errors

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding or updating tests
- `chore`: Updating build tasks, package manager configs, etc.

**Scopes**: Package names (e.g., `feat(core): add new API`)

**Examples**:
```
feat(ui-components): add Button component
fix(api-client): handle network timeout errors
docs(readme): update installation instructions
```

### Pull Request Process

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request**:
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes

3. **Address Review Comments**:
   - Make requested changes
   - Push updates to the same branch
   - Re-request review when ready

4. **Merge**:
   - Once approved, a maintainer will merge your PR
   - Delete your branch after merge

## Code Style

### General Guidelines

{{code_style_guidelines}}

### Linting

Run linters before committing:

```bash
{{lint_command}}
```

Auto-fix issues:

```bash
{{lint_fix_command}}
```

### Formatting

We use {{formatter_name}} for code formatting:

```bash
{{format_command}}
```

## Monorepo-Specific Guidelines

### Cross-Package Changes

When making changes across multiple packages:

1. Ensure version compatibility
2. Update all affected packages together
3. Test the entire workspace
4. Document breaking changes

### Build Order

Some packages depend on others. The build system handles this automatically, but be aware:

{{build_order_info}}

### Circular Dependencies

Avoid circular dependencies between packages. If you need shared code:

1. Create a new shared package
2. Move common code there
3. Have both packages depend on the shared package

## Release Process

{{release_process}}

## Getting Help

- **Questions?** Open a [Discussion]({{discussions_url}})
- **Bug?** Open an [Issue]({{issues_url}})
- **Security?** See [SECURITY.md](SECURITY.md)

## Code of Conduct

Please note that this project is released with a [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

By contributing, you agree that your contributions will be licensed under the {{license}} License.
