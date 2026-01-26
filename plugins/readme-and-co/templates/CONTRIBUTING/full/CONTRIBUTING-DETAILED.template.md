# Contributing to {{project_name}}

Thank you for your interest in contributing to {{project_name}}! We welcome contributions from the community and are grateful for your support.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## Code of Conduct

This project adheres to the Contributor Covenant [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to {{conduct_email}}.

## Getting Started

### Prerequisites

Before you begin, ensure you have:

{{prerequisites}}

### Development Environment Setup

1. **Fork and Clone**
   ```bash
   git clone {{repo_url}}/{{project_name}}.git
   cd {{project_name}}
   ```

2. **Install Dependencies**
   ```bash
   {{install_command}}
   ```

3. **Set Up Environment**
   ```bash
   {{env_setup_commands}}
   ```

4. **Verify Setup**
   ```bash
   {{verify_command}}
   ```

## How to Contribute

### Types of Contributions

We welcome many types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix bugs
- 💡 **Feature Requests**: Suggest new features or improvements
- 📖 **Documentation**: Improve or add to our documentation
- 💻 **Code**: Fix bugs or implement features
- 🧪 **Tests**: Add or improve test coverage
- 🎨 **Design**: Improve UI/UX
- 🌍 **Translations**: Help translate the project

### Reporting Bugs

Before creating bug reports:
1. **Search existing issues** to avoid duplicates
2. **Check if it's already fixed** in the latest version
3. **Gather relevant information**

When creating a bug report, include:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., macOS 13.0]
- Version: [e.g., 2.1.0]
- {{language}} Version: [e.g., {{language_version}}]

**Additional context**
Any other relevant information.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When suggesting:

1. **Use a clear title** describing the enhancement
2. **Provide detailed description** of the proposed feature
3. **Explain the motivation** - why is this useful?
4. **Describe alternatives** you've considered
5. **Include mockups** if it's a UI change

## Development Workflow

### Branch Naming

Use descriptive branch names:
- `feature/add-user-authentication`
- `bugfix/fix-memory-leak`
- `docs/update-api-reference`
- `refactor/simplify-parser`

### Development Process

1. **Create a branch** from `{{default_branch}}`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards

3. **Write/update tests** for your changes

4. **Run the test suite**
   ```bash
   {{test_command}}
   ```

5. **Update documentation** if needed

6. **Commit your changes** following commit guidelines

7. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a Pull Request**

## Coding Standards

### Style Guide

We follow {{style_guide_name}}:

{{code_style_details}}

### Code Formatting

We use automated formatters:
- **Formatter**: {{formatter_tool}}
- **Linter**: {{linter_tool}}

Run before committing:
```bash
{{format_command}}
{{lint_command}}
```

### Best Practices

- **Keep it simple**: Prefer clarity over cleverness
- **DRY principle**: Don't repeat yourself
- **Single Responsibility**: Each function/class should do one thing
- **Meaningful names**: Use descriptive variable and function names
- **Comments**: Explain *why*, not *what*
- **Error handling**: Handle errors gracefully

### Architecture Guidelines

{{architecture_guidelines}}

## Testing Guidelines

### Test Coverage

- Aim for **{{test_coverage_target}}% coverage**
- All new features **must include tests**
- Bug fixes **should include regression tests**

### Writing Tests

```{{language}}
{{test_example}}
```

### Running Tests

```bash
# Run all tests
{{test_command}}

# Run specific test file
{{test_file_command}}

# Run with coverage
{{coverage_command}}

# Run in watch mode
{{watch_command}}
```

### Test Categories

- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test complete user workflows
- **Performance Tests**: Benchmark critical paths

## Documentation

### Types of Documentation

1. **Code Comments**: Explain complex logic
2. **API Documentation**: Document public APIs
3. **User Guides**: Help users understand features
4. **Developer Guides**: Help contributors

### Documentation Style

- Use clear, simple language
- Include code examples
- Keep it up-to-date with code changes
- Add diagrams for complex concepts

### Building Documentation

```bash
{{docs_build_command}}
```

## Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(auth): add OAuth2 authentication

Implement OAuth2 flow with support for Google and GitHub providers.
Includes token refresh logic and session management.

Closes #123
```

```bash
fix(parser): handle edge case with empty input

Previously, empty input caused a null pointer exception.
Now returns an empty result gracefully.

Fixes #456
```

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guide
- [ ] Documentation is updated
- [ ] Commit messages follow convention
- [ ] Branch is up-to-date with `{{default_branch}}`

### PR Checklist

When opening a PR, use this template:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
- [ ] Follows code style
- [ ] Self-review completed
```

### Review Process

1. **Automated Checks**: CI must pass
2. **Code Review**: At least {{required_reviewers}} approval(s) required
3. **Testing**: Maintainers may test changes
4. **Merge**: Maintainer will merge when approved

### Review Timeline

We aim to:
- **Initial response**: Within 2 business days
- **Review completion**: Within 1 week
- **Merge**: After approval and CI passes

## Community

### Getting Help

- 💬 [Discussions]({{discussions_url}})
- 💼 [Slack/Discord]({{chat_url}})
- 📧 Email: {{support_email}}
- 📖 [Documentation]({{docs_url}})

### Recognition

Contributors are recognized:
- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Featured in monthly contributor spotlight

### Maintainers

Current maintainers:

{{maintainers_list}}

## License

By contributing, you agree that your contributions will be licensed under the {{license}} License.

## Questions?

Don't hesitate to ask! We're here to help:
- Open a [Discussion]({{discussions_url}})
- Email {{support_email}}
- Join our [community chat]({{chat_url}})

---

Thank you for contributing to {{project_name}}! 🎉
