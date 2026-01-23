# Settings Presets Plugin

A Claude Code plugin that streamlines initial project setup by automating common settings configurations.

## Features

- **Powerline Status Line Configuration**: Create and configure `.claude/.claude-powerline.json` with natural language commands
- **Attribution Settings Management**: Configure commit and PR attribution in `.claude/settings.local.json`
- **Smart Defaults**: Apply your preferred configuration instantly
- **Preserve Existing Settings**: Only modifies explicitly requested values
- **Safe Operations**: Creates backups before changes with confirmation workflow

## Installation

### From Marketplace

```bash
cc plugins install settings-presets
```

### Local Development

```bash
cc --plugin-dir /path/to/settings-presets
```

## Usage

### Configure Powerline Status Line

The plugin provides the `/configure-powerline` skill for setting up your status line:

**Use default configuration:**
```
/configure-powerline
```
or
```
use my default status line
configure powerline as usual
```

**Custom configurations:**
```
/configure-powerline just show the directory and context
```

```
/configure-powerline two lines. Directory (basename only) on top then all metrics below
```

```
configure powerline with rose-pine theme
```

**Ask about available options:**
```
what themes are available for powerline?
what segments can I show in the status line?
```

### Configure Attribution Settings

Manage commit and PR attribution with natural language:

**Change attribution name:**
```
Change Claude's name to Big Dawg in the Co-Authored-By
```

**Remove attribution:**
```
Remove the co-authored by
stop adding the co-authored by
```

**Update PR attribution:**
```
Change the PR attribution to say it's generated with style
```

**Customize both:**
```
Change the PR attribution to say it's generated with style and update Claude's name to match the commit attribution
```

## How It Works

Both skills follow a safe workflow:

1. Read existing configuration files
2. Create backup files (`.backup` extension)
3. Apply requested changes (preserving unmodified settings)
4. Ask for confirmation
5. Based on your response:
   - Keep changes and delete backups
   - Restore from backups and delete them

## Requirements

- Claude Code CLI
- For powerline: Node.js and npm (installed via npx automatically)

## Files Modified

- `.claude/.claude-powerline.json` - Powerline configuration
- `.claude/settings.local.json` - Claude Code settings (statusLine, attribution)

## License

MIT
