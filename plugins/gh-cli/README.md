# GitHub CLI (gh) Plugin for Claude Code

A comprehensive skill that enables Claude to autonomously create and execute GitHub workflows using the official GitHub CLI (`gh`).

## Overview

This plugin provides Claude with deep knowledge of GitHub CLI capabilities, allowing it to:
- Manage pull requests (create, review, merge, comment)
- Triage and manage issues (label, comment, close)
- Monitor and fix GitHub Actions workflows
- Execute custom GitHub API operations
- Create autonomous workflows tailored to your specific needs

## Features

- **Autonomous Workflow Creation**: Claude designs and executes multi-step GitHub workflows
- **Smart Error Handling**: Automatically diagnoses and recovers from common issues
- **Context-Aware**: Works within your current repository and respects your Claude Code mode
- **Comprehensive Coverage**: PRs, Issues, Actions, API calls, and more
- **Built-in Help Integration**: Leverages `gh --help` for up-to-date command information

## Prerequisites

### Required
- **GitHub CLI installed**: Install from https://cli.github.com/
  - macOS: `brew install gh`
  - Linux: See [installation guide](https://github.com/cli/cli#installation)
  - Windows: See [installation guide](https://github.com/cli/cli#installation)

- **Authentication**: Run `gh auth login` to authenticate with GitHub
  - Supports both GitHub.com and GitHub Enterprise Server
  - Creates token with appropriate scopes automatically

### Optional
- Git repository context for repo-specific operations
- Appropriate GitHub permissions for actions Claude will perform

## Installation

### From Local Directory

```bash
# Install plugin locally
cp -r gh-cli ~/.claude-plugin/gh-cli

# Or use with --plugin-dir flag
claude --plugin-dir /path/to/gh-cli
```

### Verification

After installation, verify the skill loaded:
1. Start a Claude Code session
2. Ask: "Can you help me create a pull request using GitHub CLI?"
3. Claude should recognize the GitHub CLI context and activate the skill

## Usage

### Common Workflows

**Check and fix failing CI/CD:**
```
"Check the failing GitHub Actions run and help me fix the problems"
```

**Triage new issues:**
```
"Triage the new issues in this repository - label them appropriately and add initial responses"
```

**Create a pull request:**
```
"Create a PR for my current branch with a description of the changes"
```

**Implement PR feedback:**
```
"Review the comments on PR #123 and implement the requested changes"
```

### How It Works

Claude will:
1. **Understand context**: Verify repository and authentication status
2. **Design workflow**: Create a multi-step plan for your request
3. **Execute autonomously**: Run `gh` commands with proper error handling
4. **Adapt to mode**: Respect your current Claude Code mode (accept edits vs plan mode)
5. **Confirm destructive actions**: Ask before closing issues, deleting branches, etc.

### Error Recovery

If something goes wrong, Claude will:
1. Review command output for error messages
2. Search troubleshooting documentation for known issues
3. Verify command syntax against `gh --help`
4. Report detailed diagnostics and ask for your guidance

## Skill Trigger Phrases

The skill activates when you mention:
- GitHub CLI, gh command, or gh tool
- GitHub operations (pull requests, issues, actions, releases)
- Repository workflows and automation
- GitHub API interactions

## Examples

See `skills/github-cli/examples/` for real-world scenarios including:
- Complete CI/CD debugging workflows
- Issue triage automation
- PR review and merge processes
- Custom API operation patterns

## Troubleshooting

**Skill not activating:**
- Ensure plugin is properly installed
- Try explicitly mentioning "GitHub CLI" or "gh command"
- Restart Claude Code session

**Authentication errors:**
- Run `gh auth status` to check authentication
- Re-authenticate with `gh auth login`
- Check token permissions at https://github.com/settings/tokens

**Permission errors:**
- Verify you have appropriate repository permissions
- Check organization settings if working with org repos
- Ensure token has required scopes (repo, workflow, etc.)

## Contributing

This plugin is designed to evolve with your workflows. Consider:
- Adding new workflow patterns to `common-patterns.md`
- Documenting edge cases in `troubleshooting.md`
- Sharing successful automation patterns

## Resources

- [GitHub CLI Manual](https://cli.github.com/manual)
- [GitHub CLI Repository](https://github.com/cli/cli)
- [GitHub API Documentation](https://docs.github.com/en/rest)

## License

MIT

## Version

0.1.0 - Initial release
