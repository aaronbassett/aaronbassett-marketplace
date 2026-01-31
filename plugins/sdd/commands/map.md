---
description: Map codebase into 8 specialized documents using parallel mapper agents. Supports full remap, incremental update, and skip modes.
handoffs:
  - label: Continue to Planning
    agent: sdd:plan
    prompt: Create implementation plan using codebase documents
    send: true
  - label: Continue to Specification
    agent: sdd:specify
    prompt: Create feature specification
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

This command orchestrates 4 parallel mapper agents to generate 8 codebase documents:

| Focus | Agent | Documents Generated |
|-------|-------|---------------------|
| tech | sdd:code-mapper | STACK.md, INTEGRATIONS.md |
| arch | sdd:code-mapper | ARCHITECTURE.md, STRUCTURE.md |
| conventions | sdd:code-mapper | CONVENTIONS.md, TESTING.md |
| security | sdd:code-mapper | SECURITY.md, CONCERNS.md |

All documents are written to `.sdd/codebase/`.

## Execution Steps

### 1. Parse Arguments and Determine Mode

Check `$ARGUMENTS` for mode specification:

| Argument | Mode | Description |
|----------|------|-------------|
| `full` | Full Remap | Regenerate all 8 documents |
| `incremental` | Incremental | Update only changed areas |
| `skip` | Skip | Don't run mapping |
| (empty) | Auto-detect | Check if docs exist to determine mode |

**Auto-detect logic:**
- If `.sdd/codebase/` doesn't exist or is empty → Full mode
- If codebase docs exist → Offer choice: Refresh, Update, Skip

### 2. Brownfield Detection (for Full mode)

For new or full remapping, detect if this is a brownfield project:

```bash
# Check for existing code
find . -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.rs" -o -name "*.go" | head -5
```

```bash
# Check for package manifests
ls package.json Cargo.toml pyproject.toml go.mod 2>/dev/null
```

**If brownfield (existing code found):**
- Inform user that existing codebase was detected
- Full mapping will analyze existing code
- Documents will reflect current state

**If greenfield (no code found):**
- Inform user that no existing code was detected
- Documents will be minimal/templated
- Suggest running again after initial development

### 3. Ensure Output Directory Exists

```bash
mkdir -p .sdd/codebase
```

### 4. Launch Parallel Mapper Agents

Launch 4 instances of `sdd:code-mapper` agent in parallel (single message, multiple Task calls):

**Agent 1 - Tech Mapper:**
```
Task(
  subagent_type="sdd:code-mapper",
  description="Map tech stack and integrations",
  prompt="Focus: tech

          Project root: {PROJECT_ROOT}

          Analyze this codebase for technology stack and external integrations.
          Use the sdd:code-mapping skill to get templates and analysis guidance.
          Write documents directly to .sdd/codebase/.
          Return confirmation only: file paths + line counts."
)
```

**Agent 2 - Architecture Mapper:**
```
Task(
  subagent_type="sdd:code-mapper",
  description="Map architecture and structure",
  prompt="Focus: arch

          Project root: {PROJECT_ROOT}

          Analyze this codebase for architecture patterns and directory structure.
          Use the sdd:code-mapping skill to get templates and analysis guidance.
          Write documents directly to .sdd/codebase/.
          Return confirmation only: file paths + line counts."
)
```

**Agent 3 - Conventions Mapper:**
```
Task(
  subagent_type="sdd:code-mapper",
  description="Map conventions and testing",
  prompt="Focus: conventions

          Project root: {PROJECT_ROOT}

          Analyze this codebase for coding conventions and testing patterns.
          Use the sdd:code-mapping skill to get templates and analysis guidance.
          Write documents directly to .sdd/codebase/.
          Return confirmation only: file paths + line counts."
)
```

**Agent 4 - Security Mapper:**
```
Task(
  subagent_type="sdd:code-mapper",
  description="Map security and concerns",
  prompt="Focus: security

          Project root: {PROJECT_ROOT}

          Analyze this codebase for security patterns and known concerns.
          Use the sdd:code-mapping skill to get templates and analysis guidance.
          Write documents directly to .sdd/codebase/.
          Return confirmation only: file paths + line counts."
)
```

### 5. Collect Results

Wait for all 4 agents to complete. Collect:
- File paths created/updated
- Line counts for each file
- Any errors reported

### 6. Structure Drift Detection (Incremental mode)

For incremental mode, compare current state to previous:

**Load Previous State:**
- Read existing `.sdd/codebase/*.md` files
- Extract key information (technologies, patterns, structure)

**Compare to Current:**
- Run abbreviated analysis to detect changes
- Score changes using drift criteria

**Drift Scoring:**

| Change Type | Score |
|-------------|-------|
| New major dependency | +3 |
| Directory restructure | +3 |
| Architecture pattern change | +5 |
| Security model change | +5 |
| Testing strategy change | +2 |

**Generate Drift Report:**

```markdown
## Drift Report

**Comparison**: {previous timestamp} → {current timestamp}
**Overall Score**: {N}

### Document Changes

| Document | Change Type | Details | Score |
|----------|-------------|---------|-------|
| ARCHITECTURE.md | Major | REST → GraphQL | +5 |
| TESTING.md | Minor | Added E2E framework | +2 |

### Affected Plan Sections
- {list of plan sections that may need updates}

### Affected Task Categories
- {list of task categories that may need updates}

### Recommendation
{STRUCTURE_DRIFT_ALERT or STRUCTURE_DRIFT_CRITICAL if score >= 5 or >= 8}
```

### 7. Handle Drift Alerts

**If score >= 5 (STRUCTURE_DRIFT_ALERT):**
- Suggest running `/sdd:plan --drift` to update plan
- Don't block, just recommend

**If score >= 8 (STRUCTURE_DRIFT_CRITICAL):**
- Strongly recommend `/sdd:plan --drift && /sdd:tasks --drift`
- Pause implementation if detected mid-phase
- Ask user how to proceed

### 8. Report Completion

Output summary:

```markdown
## Codebase Mapping Complete

**Mode**: {Full/Incremental}
**Documents Generated**: 8

### Files Created/Updated

| Document | Lines | Status |
|----------|-------|--------|
| .sdd/codebase/STACK.md | {N} | ✓ |
| .sdd/codebase/INTEGRATIONS.md | {N} | ✓ |
| .sdd/codebase/ARCHITECTURE.md | {N} | ✓ |
| .sdd/codebase/STRUCTURE.md | {N} | ✓ |
| .sdd/codebase/CONVENTIONS.md | {N} | ✓ |
| .sdd/codebase/TESTING.md | {N} | ✓ |
| .sdd/codebase/SECURITY.md | {N} | ✓ |
| .sdd/codebase/CONCERNS.md | {N} | ✓ |

{Drift Report if incremental mode}

### Next Steps

- Run `/sdd:specify` to create feature specifications
- Run `/sdd:plan` to create implementation plans
- Codebase documents will inform all downstream commands
```

## Incremental Mode Details

When running in incremental mode (e.g., at end of implementation phase):

1. **Selective Agent Spawning**: Only spawn agents for focus areas that likely changed
2. **Preserve Unchanged**: Keep document sections that haven't changed
3. **Merge Updates**: Add new findings to existing documents
4. **Track History**: Add "Last Updated" timestamp

**Trigger Detection for Incremental:**
- New dependencies in package.json/Cargo.toml
- New files in key directories
- Modified configuration files
- Changes to authentication code

## Error Handling

**If agent fails:**
- Report which focus area failed
- Continue with successful agents
- Suggest re-running for failed focus

**If all agents fail:**
- Report error with details
- Suggest checking project structure
- Offer to run in verbose mode for debugging

## Usage Examples

```bash
# Auto-detect mode
/sdd:map

# Force full remap
/sdd:map full

# Incremental update (after implementation phase)
/sdd:map incremental

# Skip mapping
/sdd:map skip
```

## Integration Points

**Called by:**
- `/sdd:specify` - After spec creation (brownfield detection)
- `/sdd:implement` - At end of each phase (incremental)
- Manual invocation

**Feeds into:**
- `/sdd:plan` - Uses all 8 documents for context
- `/sdd:tasks` - References tech stack for task generation
- `/sdd:implement` - Loads documents for agent context
- `/sdd:analyze` - Checks consistency across documents
