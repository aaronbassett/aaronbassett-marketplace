# Constitution Plugin

Create, validate, and enforce project constitutions with living governance.

Transform your project's principles from static documents into an actively enforced governance system with version tracking, automated validation, and compliance hooks.

## Features

### 1. Constitution Writer
Create a comprehensive project constitution based on your project's characteristics and requirements.

**Usage:**
```bash
Invoke the constitution:writer skill
```

### 2. Checklist Generator
Distill constitutional principles into 6-12 actionable verification tasks with semantic deduplication.

**Usage:**
```bash
Invoke the constitution:checklist-generator skill
```

**Features:**
- Combines related principles into single actionable items
- Preserves existing checklist customizations
- Removes outdated items automatically
- Adds new items from amended principles

### 3. Amendment System
Update your constitution with semantic versioning and changelog tracking.

**Usage:**
```bash
Invoke the constitution:amend skill
```

**Versioning:**
- **MAJOR (X.0.0)**: Breaking changes, removed principles
- **MINOR (X.Y.0)**: New principles added
- **PATCH (X.Y.Z)**: Clarifications and fixes

### 4. Constitution Reviewer
Automated code review against constitutional principles with severity ratings.

**Usage:**
```bash
# Review staged changes (most common)
Invoke the constitution-reviewer agent with --scope staged

# Review all uncommitted changes
Invoke the constitution-reviewer agent with --scope diff

# Review entire project
Invoke the constitution-reviewer agent with --scope full

# Review GitHub PR
Invoke the constitution-reviewer agent with --scope pr --pr 123
```

**Severity Levels:**
- **CRITICAL**: Security issues, data loss risks
- **MODERATE**: Quality issues, missing tests
- **MINOR**: Style violations, conventions

### 5. Stop Hooks
Automatic enforcement that blocks session end if changes haven't been validated.

**Behavior:**
- Detects code changes via git
- Requires constitution review before stopping
- Allows doc-only changes without review
- Prevents infinite loops with `stop_hook_active` flag

## Workflow Example

```bash
# 1. Create initial constitution
Invoke the constitution:writer skill

# 2. Generate implementation checklist
Invoke the constitution:checklist-generator skill

# 3. Make code changes
# ... edit files ...

# 4. Review against constitution (triggered by stop hook)
Invoke the constitution-reviewer agent with --scope staged

# 5. Fix any violations
# ... address reported issues ...

# 6. Amend constitution if needed
Invoke the constitution:amend skill

# Checklist automatically regenerated after amendment
```

## Integration Points

- **Amendment → Checklist**: Amendments automatically trigger checklist regeneration
- **Stop Hook → Reviewer**: Hook suggests running reviewer when blocking
- **Reviewer → Hook**: Reviewer sets flag to bypass hook (prevents infinite loop)

## Version History

See `## Changelog` section in your project's CONSTITUTION.md for amendment history.
