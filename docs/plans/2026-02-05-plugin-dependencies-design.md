# Plugin Dependency Management System

**Date:** 2026-02-05
**Status:** Draft

## Overview

A system for declaring, checking, and discovering dependencies between Claude Code plugins. Enables plugins to declare requirements on other plugins and system tools, with tooling to verify dependencies are satisfied and help generate dependency manifests for existing plugins.

## Problem

- Plugins can depend on other plugins (e.g., `sdd` requires `bug-fixes` for CPR resolver)
- Dependencies are currently documented in READMEs only - not machine-readable
- No way to verify all dependencies are installed and enabled
- No tooling to help discover what dependencies a plugin needs

## Solution

1. **`extends-plugin.json`** - Machine-readable dependency manifest alongside `plugin.json`
2. **`utils` plugin** - Two skills for dependency management:
   - `/utils:dependency-checker` - Verify dependencies are satisfied
   - `/utils:dependency-scanner` - Discover and generate dependency manifests

---

## File Format: `extends-plugin.json`

Lives alongside `plugin.json` in `.claude-plugin/`:

```
my-plugin/
├── .claude-plugin/
│   ├── plugin.json           # existing - core metadata
│   └── extends-plugin.json   # new - dependencies
└── skills/
```

### Schema

```json
{
  "dependencies": {
    "bug-fixes": "^0.3.0",
    "other-plugin@specific-marketplace": {
      "version": ">=1.0.0",
      "help": "Available from cool-marketplace:\n\n/plugin marketplace add cool/cool-marketplace\n/plugin install other-plugin@cool-marketplace"
    }
  },
  "optionalDependencies": {
    "nice-to-have": "^2.0.0"
  },
  "systemDependencies": {
    "gh": {
      "version": ">=2.0.0",
      "help": "The GitHub CLI. See https://cli.github.com/ for installation instructions"
    },
    "git": ">=2.30.0"
  },
  "optionalSystemDependencies": {
    "rg": {
      "version": ">=13.0.0",
      "help": "ripgrep - https://github.com/BurntSushi/ripgrep#installation"
    }
  }
}
```

### Rules

- **Plugin references:** `name` or `name@marketplace`
  - `name` alone matches any marketplace (plugin names are globally unique when installed)
  - `name@marketplace` enforces specific source
- **Version constraints:** npm semver syntax (`^`, `~`, `>=`, `<`, `||`, etc.)
- **Dependency value:** Either:
  - `string` - version constraint (e.g., `"^0.3.0"`)
  - `object` - `{ "version": "^0.3.0", "help": "..." }`
- **All four keys are optional** - file can contain just what's needed
- **`help` field** - displayed in resolution steps when dependency not satisfied

---

## Plugin Structure: `utils`

```
plugins/utils/
├── .claude-plugin/
│   └── plugin.json
├── scripts/
│   ├── dependency-checker.py    # collects data → JSON
│   ├── dependency-scanner.py    # pattern matches → JSON
│   ├── table-renderer.py        # JSON → ASCII tables
│   └── resolution-steps.py      # JSON → actionable steps
├── skills/
│   ├── dependency-checker/
│   │   └── SKILL.md
│   └── dependency-scanner/
│       └── SKILL.md
└── README.md
```

---

## Skill: `/utils:dependency-checker`

Checks dependencies declared in `extends-plugin.json` files against installed/enabled plugins.

### Data Sources

| File | Purpose |
|------|---------|
| `~/.claude/plugins/installed_plugins.json` | Is plugin installed? What version? |
| `~/.claude/settings.json` → `enabledPlugins` | Is plugin enabled? |
| `~/.claude/plugins/known_marketplaces.json` | Marketplace locations |
| `{marketplace}/.claude-plugin/marketplace.json` | Available plugins |
| `{plugin}/.claude-plugin/extends-plugin.json` | Declared dependencies |

### Flags

| Command | Checks |
|---------|--------|
| `dependency-checker.py` | All enabled plugins |
| `dependency-checker.py --installed` | All installed plugins (enabled + disabled) |
| `dependency-checker.py --all` | All plugins in all known marketplaces |
| `dependency-checker.py --plugin sdd` | Just sdd |
| `dependency-checker.py --installed --plugin sdd` | Just sdd (if installed) |
| `dependency-checker.py --all --plugin sdd` | Just sdd (any marketplace) |

### Output JSON

```json
{
  "checkedScope": "enabled",
  "checkedPlugin": null,
  "dependencies": [
    {
      "plugin": "bug-fixes",
      "marketplace": "aaronbassett-marketplace",
      "dependent": "sdd@aaronbassett-marketplace",
      "requiredVersion": "^0.3.0",
      "installed": true,
      "enabled": true,
      "installedVersion": "0.3.1",
      "valid": true,
      "help": null
    }
  ],
  "optionalDependencies": [],
  "systemDependencies": [
    {
      "command": "gh",
      "dependent": "git-lovely@aaronbassett-marketplace",
      "requiredVersion": ">=2.0.0",
      "installed": true,
      "installedVersion": "2.45.0",
      "valid": true,
      "help": "The GitHub CLI. See https://cli.github.com/"
    }
  ],
  "optionalSystemDependencies": []
}
```

### Workflow

1. Run `dependency-checker.py [flags] > /tmp/dependency-check.json`
2. Run `table-renderer.py /tmp/dependency-check.json` → displays tables
3. Run `resolution-steps.py /tmp/dependency-check.json` → displays resolution steps (if issues)
4. Read `/tmp/dependency-check.json` for additional context if needed

### Table Output

```
┌─────────────┬─────────────┬───────────────────────┬─────────┬───────────┬─────────┬─────────┬───────┬───────────────────────┐
│   plugin    │ marketplace │       dependent       │ version │ installed │ enabled │ version │ valid │         notes         │
├─────────────┼─────────────┼───────────────────────┼─────────┼───────────┼─────────┼─────────┼───────┼───────────────────────┤
│ hello-world │ cool-skills │ greeting@my-skills    │ ^2.2.0  │ ✓         │ x       │   2.2.3 │ no    │ marketplace available │
│ goodbye     │ cool-skills │ cya@my-skills         │ ^0.1.0  │ ✓         │ ✓       │   0.1.2 │ yes   │ marketplace available │
└─────────────┴─────────────┴───────────────────────┴─────────┴───────────┴─────────┴─────────┴───────┴───────────────────────┘
```

- Only renders non-empty tables
- Separate tables for: dependencies, optionalDependencies, systemDependencies, optionalSystemDependencies

### Resolution Steps

| Issue | Resolution |
|-------|------------|
| Marketplace not known | `/plugin marketplace add owner/repo` |
| Not installed | `/plugin install name@marketplace` |
| Installed but not enabled | "Enable via `/plugin` TUI" |
| Wrong version (newer available) | `/plugin update name@marketplace` |
| Wrong version (none available) | Check remote for latest version |
| System dep not installed | Display `help` text or generic guidance |
| System dep wrong version | "Update {command} to {version}" |

Remote version check: Only performed when local version doesn't satisfy requirement.

---

## Skill: `/utils:dependency-scanner`

Scans plugins to discover dependencies and generate draft `extends-plugin.json` files.

### Flags

| Command | Scans |
|---------|-------|
| `dependency-scanner.py` | All enabled plugins |
| `dependency-scanner.py --plugin sdd` | Just sdd (installed) |
| `dependency-scanner.py --marketplace aaronbassett-marketplace` | All plugins from that marketplace |
| `dependency-scanner.py --plugin-dir /path/to/plugin` | Local plugin directory (not installed) |
| `dependency-scanner.py --marketplace-dir /path/to/marketplace` | Local marketplace directory (not installed) |

### Pattern Matching

The script does pattern matching only - returns potential matches for LLM interpretation:

| Type | Patterns |
|------|----------|
| `skillReference` | `/plugin:skill`, `/skill`, `Skill tool`, `invoke skill`, `use skill`, `use the X skill`, `X skill`, `run skill`, `call skill`, `trigger skill`, `execute skill`, `launch skill`, `run command`, `use command`, `execute command`, `invoke command`, `/command` |
| `agentReference` | `@agent`, `subagent`, `sub-agent`, `Task tool`, `launch agent`, `spawn agent`, `use agent`, `X agent`, `agent to`, `subagent_type` |
| `systemCommand` | backticks containing commands, `Bash tool`, `run X`, `execute X`, `call X`, `use X to`, `which X`, `X --version`, `X -v`, shebang lines `#!/usr/bin/env X`, `import X` (Python), `require X` (JS) |
| `toolReference` | `use the X tool`, `X tool`, `call tool`, `invoke tool`, `PreToolUse`, `PostToolUse` |
| `pluginReference` | `X plugin`, `requires X`, `depends on X`, `install X`, `needs X`, `prerequisite`, `dependency` |

**Files scanned:**
- SKILL.md files
- Agent definitions
- README.md
- Shell scripts in `scripts/`
- YAML frontmatter
- JSON in skills/agents
- Code blocks (triple backticks)
- Inline code (single backticks)

**Principle:** Better to have false positives than miss dependencies. LLM filters noise.

### Scanner Output JSON

```json
[
  {
    "scannedPlugin": "sdd",
    "scannedMarketplace": "aaronbassett-marketplace",
    "location": "/path/to/skills/foo/SKILL.md:42:17",
    "matched": "use the bug-fixes:find-claude-plugin-root skill",
    "type": "skillReference"
  },
  {
    "scannedPlugin": "sdd",
    "scannedMarketplace": "aaronbassett-marketplace",
    "location": "/path/to/skills/bar/SKILL.md:87:5",
    "matched": "`gh pr create`",
    "type": "systemCommand"
  }
]
```

### SKILL.md Workflow

1. Run `dependency-scanner.py` → get raw matches
2. Filter out internal references (skill A in plugin A referencing skill B in plugin A)
3. Group matches by likely source:
   - `/foo:create`, `/foo:bar` → group as "foo" plugin
   - `gh pr`, `gh issue` → group as "gh" system dep
4. For each group, determine source:
   - Plugin: search installed plugins, available skills
   - System: run `which X`, `X --version`, web search for install docs
5. **Batch AskUserQuestion** per group:
   ```
   Found 3 skills (spam, ham, eggs) from foo@bar-marketplace.
   Current installed version: 1.2.3
   Add to dependencies?
   - Yes, require ^1.2.0
   - Yes, require ^1.0.0
   - Yes, as optional dependency
   - No, skip this
   ```
6. Build `extends-plugin.json` from confirmed answers
7. Show final draft, confirm before writing

### Key Principles

- Script does dumb pattern matching
- LLM interprets, groups, researches
- User confirms everything via batched questions
- Never auto-write `extends-plugin.json`

---

## Technical Notes

### Plugin Installation Model

- Plugin keys in `installed_plugins.json`: `{plugin-name}@{marketplace-name}`
- Plugin names are globally unique - Claude Code prevents installing same-named plugins from different marketplaces
- `scope: "user"` = global install, `scope: "local"` = project-specific
- Enabled state tracked in `~/.claude/settings.json` → `enabledPlugins`

### Semver

Uses npm semver semantics: https://semver.npmjs.com/

### Why Separate File

`extends-plugin.json` lives alongside `plugin.json` rather than extending it because:
- Unknown fields in `plugin.json` may cause validation errors/warnings
- Forward compatibility with future Claude Code changes
- Clear separation of concerns

---

## Implementation Order

1. Create `utils` plugin scaffold
2. Implement `dependency-scanner.py` and `/utils:dependency-scanner` skill
3. Use scanner to generate `extends-plugin.json` for existing plugins (especially `sdd` → `bug-fixes`)
4. Implement `dependency-checker.py`, `table-renderer.py`, `resolution-steps.py`
5. Implement `/utils:dependency-checker` skill
6. Add `extends-plugin.json` to marketplace validation (optional)
