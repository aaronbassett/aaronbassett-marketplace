---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
handoffs:
  - label: Create Tasks
    agent: sdd:tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: sdd:checklist
    prompt: Create a checklist for the following domain...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Setup

Before executing this command, resolve the plugin root path for accessing scripts:

```bash
# Invoke CPR resolver to create /tmp/cpr.py
Skill(skill="utils:find-claude-plugin-root")

# Then use it to resolve plugin paths
PLUGIN_ROOT=$(python3 /tmp/cpr.py sdd)
```

## Outline

1. **Setup**: Discover feature directory and determine planning mode (initial vs incremental vs drift):

   a. **Find Feature Directory**:
      1. Use Bash to get current git branch: `git branch --show-current`
      2. Extract feature number prefix (e.g., "004" from "004-user-auth")
      3. Use Glob to find specs directory: `specs/{number}*/` where number matches prefix
      4. Store as FEATURE_DIR (absolute path)

   b. **Check for --drift Mode**:
      - If `$ARGUMENTS` contains `--drift`, enter Drift Update Mode (see section below)
      - Drift mode is triggered when codebase mapping detects structure changes

   c. **Determine Planning Mode**:
      - Use Glob to check if `{FEATURE_DIR}/plan.md` exists

      **If plan.md does NOT exist (First Run)**:
      1. Run `"$PLUGIN_ROOT"/skills/sdd-infrastructure/scripts/setup-plan.sh --json` from repo root
      2. Parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH
      3. Use escape syntax for single quotes: `'I'\''m Groot'` (or double-quote: `"I'm Groot"`)
      4. Script creates plan.md from template
      5. Proceed to step 2 (Load context)

      **If plan.md EXISTS (Incremental Run)**:
      1. Use Read to load existing `{FEATURE_DIR}/plan.md`
      2. Use Read to load `{FEATURE_DIR}/spec.md`
      3. Identify what changed in spec since last planning:
         - New requirements added
         - Success criteria modified
         - User scenarios changed
         - Non-functional requirements updated
      4. Use Read to load codebase documents from `.sdd/codebase/`:
         - STACK.md for tech stack
         - ARCHITECTURE.md for system design
         - STRUCTURE.md for directory layout
         - CONVENTIONS.md for code patterns
      5. Determine which plan sections need updates:
         - If spec requirements changed → Update Technical Context, Phases
         - If success criteria changed → Update Constitution Check
         - If tech stack changed → Update Technical Context
         - If data model affected → Update Phase 1 data-model.md reference
      6. Use Edit to update ONLY affected sections in plan.md
      7. Preserve existing research.md, data-model.md, contracts/ unless explicitly changing
      8. Skip to step 3 (Execute plan workflow) with targeted updates only

   **Benefits of Incremental Planning**:
   - Can refine plan without starting from scratch
   - Preserves completed research and design artifacts
   - Faster iteration on spec changes
   - Maintains continuity across planning sessions

   **Drift Update Mode** (`--drift`):
   When structure drift is detected by `/sdd:map`, this mode updates only affected sections:

   1. **Load Drift Report** from `/sdd:map` output:
      - Which codebase documents changed (ARCHITECTURE.md, TESTING.md, etc.)
      - What specifically changed (new framework, dir restructure, etc.)
      - Drift score and category

   2. **Map Drift to Plan Sections**:

      | Codebase Doc Changed | Plan Sections to Update |
      |---------------------|------------------------|
      | ARCHITECTURE.md | Technical Context, Phase 1 (contracts), data-model.md |
      | STRUCTURE.md | File paths in all phases, project structure references |
      | STACK.md | Technical Context (dependencies), Phase 2 (tooling) |
      | TESTING.md | Phase 2 (test framework), test task references |
      | SECURITY.md | Constitution check, security-related tasks |
      | CONVENTIONS.md | Coding style references, linting config |
      | INTEGRATIONS.md | API contracts, external service references |

   3. **Incremental Edit Process**:
      - Use Read to load existing plan.md
      - Use Edit to update ONLY sections mapped to changed docs
      - Preserve unchanged sections verbatim
      - Add "Drift Update" entry to plan history with timestamp + changes

   4. **Regenerate Affected Artifacts**:
      - If ARCHITECTURE changed → Regenerate data-model.md, contracts/
      - If STRUCTURE changed → Update file paths in quickstart.md
      - If TESTING changed → Update test commands in quickstart.md

2. **Load context**: Read the following documents for planning context:
   - FEATURE_SPEC (spec.md)
   - `.sdd/memory/constitution.md`
   - Codebase documents from `.sdd/codebase/`:
     - STACK.md - for technology decisions
     - ARCHITECTURE.md - for system design context
     - STRUCTURE.md - for directory layout guidance
     - CONVENTIONS.md - for code patterns
     - TESTING.md - for test strategy
     - SECURITY.md - for security requirements
     - INTEGRATIONS.md - for external service context
     - CONCERNS.md - for known issues and debt
   - If first run, load IMPL_PLAN template (already copied by setup-plan.sh).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Phase 1: Update agent context by running the agent script
   - Phase 2: Set up local development environment (linting, formatting, testing)
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 (dev environment setup). Report branch, IMPL_PLAN path, generated artifacts, and tooling status.

## Phases

### Pre-Phase: Learn from Previous Retros

**Purpose**: Build on project learning and avoid repeating mistakes from previous features.

1. **Discover Previous Retros**:
   - Use Glob to find all retrospective files: `specs/*/retro/*.md`
   - Sort by modification time (most recent first)
   - Select last 3-5 features for analysis

2. **Extract Relevant Learnings** (if retros exist):
   - Use Read to load each retro file
   - Extract items from each section:
     - **What Worked Well**: Effective patterns, successful approaches, helpful tools
     - **What Didn't Work**: Problems encountered, limitations, failed approaches
     - **Workarounds & Solutions**: Bug fixes, non-obvious solutions, clever workarounds
     - **Packages & Dependencies**: Useful packages discovered, packages to avoid, version issues
     - **Patterns & Code**: Reusable patterns, architectural insights
     - **For Next Time**: Improvement suggestions, lessons learned

3. **Categorize Learnings by Relevance**:
   - **Tech Stack Decisions**: Technologies that worked well/poorly in similar contexts
   - **Architecture Patterns**: Successful patterns for similar feature types
   - **Dependencies**: Packages worth using/avoiding for current tech stack
   - **Known Issues**: Workarounds for bugs or limitations in current stack
   - **Best Practices**: Patterns that emerged across multiple features

4. **Incorporate into Planning**:
   - Add relevant tech decisions to Technical Context
   - Reference successful patterns in architecture decisions
   - Note dependencies to prefer/avoid in research.md
   - Document known issue workarounds in research.md
   - Use learnings to inform Phase 0 research questions

**Benefits**:
- Avoid repeating mistakes from previous features
- Reuse successful patterns and approaches
- Faster decision-making with historical context
- Build institutional knowledge over time

**Output**: Context-aware planning that builds on project experience

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Agent context update** (using Claude Code tools for accuracy):

   a. **Extract Tech Stack from Codebase Documents**:
      - Use Read to load `.sdd/codebase/STACK.md` for comprehensive tech stack
      - Extract:
        - Languages & Runtimes
        - Frameworks
        - Critical Dependencies
        - Build Tools
      - If STACK.md doesn't exist, fall back to extracting from plan.md

   b. **Detect Agent Platform**:
      - Check for `.claude/` directory → Claude Code
      - Check for `.cursor/` directory → Cursor
      - Check for `.aider/` directory → Aider
      - Check for `.windsurf/` directory → Windsurf

   c. **Update Agent Context File**:
      - **For Claude Code**: Use Read to load `CLAUDE.md` in repo root
      - Use Edit to update specific sections:
        - Replace "Active Technologies" section with current tech stack
        - Append to "Recent Changes" section with timestamp
        - Update "File Structure" if project structure changed
      - Preserve content between custom markers (e.g., `<!-- MANUAL ADDITIONS START -->`)

   d. **Generate Tech-Specific Commands** (using skills):
      - For each detected technology, invoke relevant skill to suggest commands:
        - TypeScript project: Use devs:typescript-core
          - Prompt: "What are the key TypeScript/Node.js commands developers should know for this project structure?"
        - Python/FastAPI project: Use devs:python-core
          - Prompt: "What are essential Python/FastAPI commands for this project?"
        - Rust project: Use devs:rust-core
          - Prompt: "What are critical Rust/Cargo commands for this project?"
        - Next.js project: Use devs:react-core
          - Prompt: "What are important Next.js commands for this app structure?"
      - Add skill-generated commands to appropriate section in CLAUDE.md

   e. **Validation**:
      - Use Read to verify updates were applied correctly
      - Check that manual additions were preserved
      - Ensure tech stack is accurately represented

   **Benefits over bash script**:
   - More accurate tech stack extraction (semantic understanding vs regex)
   - Skills provide context-aware, project-specific commands (not generic)
   - Edit tool is more reliable than sed for updating sections
   - Can detect and preserve manual additions intelligently
   - Validates changes were applied correctly

**Output**: data-model.md, /contracts/*, quickstart.md, updated CLAUDE.md (or agent-specific file)

### Phase 2: Local Development Environment Setup

**Prerequisites:** Tech stack determined (from `.sdd/codebase/STACK.md` or plan.md Technical Context)

**Purpose**: Establish consistent, automated development tooling that enforces code quality from the start.

1. **Analyze Project Structure**:
   - Use Glob to detect existing config files:
     - `package.json`, `tsconfig.json`, `biome.json`, `.eslintrc*` → JavaScript/TypeScript
     - `Cargo.toml`, `rustfmt.toml`, `clippy.toml` → Rust
     - `pyproject.toml`, `setup.py`, `ruff.toml` → Python
   - Detect workspace/monorepo patterns:
     - `pnpm-workspace.yaml`, `packages/*/package.json` → pnpm workspaces
     - `lerna.json`, `nx.json` → JS monorepo tools
     - `Cargo.toml` with `[workspace]` → Rust workspace
     - `pyproject.toml` with workspace config → Python monorepo

2. **Invoke Init-Local-Tooling Skill**:
   - Use the Skill tool to invoke `/dev-specialisms:init-local-tooling` with detected context:
     ```
     Skill: init-local-tooling
     Args: "{language} project in {FEATURE_DIR}, {monorepo_type if detected}"
     ```
   - The skill handles:
     - **Linting**: ESLint/Biome (JS/TS), clippy (Rust), ruff (Python)
     - **Formatting**: Prettier/Biome (JS/TS), rustfmt (Rust), ruff/black (Python)
     - **Type Checking**: tsc strict mode (TS), mypy/pyright (Python)
     - **Testing**: Vitest/Jest (JS/TS), cargo test (Rust), pytest (Python)
     - **Git Hooks**: husky + lint-staged, pre-commit hooks
     - **Editor Config**: .editorconfig, VS Code settings

3. **Stack-Specific Configuration** (supplement skill output):

   a. **TypeScript/JavaScript**:
      - Ensure `tsconfig.json` has strict mode enabled
      - Configure path aliases matching project structure
      - Set up build/dev scripts in package.json
      - Configure test coverage thresholds if specified in constitution

   b. **Rust**:
      - Configure clippy lints in `Cargo.toml` or `clippy.toml`
      - Set up `rustfmt.toml` with team preferences
      - Configure test organization (unit vs integration)
      - Set up cargo-watch for development

   c. **Python**:
      - Configure ruff rules matching constitution standards
      - Set up mypy/pyright with appropriate strictness
      - Configure pytest with coverage and markers
      - Set up virtual environment management (venv, poetry, uv)

   d. **Monorepo/Workspace**:
      - Configure shared lint/format configs at root
      - Set up workspace-aware scripts
      - Configure selective test running per package
      - Ensure consistent tool versions across packages

4. **CI/CD Integration Check**:
   - Use Glob to find CI config: `.github/workflows/*.yml`, `.gitlab-ci.yml`, etc.
   - Verify local tooling commands match CI commands
   - If no CI exists, note as "NEEDS: CI pipeline setup" in plan.md
   - Ensure test commands produce CI-compatible output

5. **Validation**:
   - Run lint command and verify it passes (or document existing issues)
   - Run format check (not auto-fix) to assess current state
   - Run type check if applicable
   - Run test suite to establish baseline
   - Document any failures as "Tech Debt" items in plan.md

6. **Update Documentation**:
   - Add setup instructions to quickstart.md:
     ```markdown
     ## Development Setup

     ### Prerequisites
     - {runtime} {version}
     - {package manager}

     ### Install Dependencies
     {install command}

     ### Available Scripts
     - `{lint}` - Run linter
     - `{format}` - Format code
     - `{typecheck}` - Run type checker
     - `{test}` - Run tests
     - `{dev}` - Start development server
     ```
   - Update CLAUDE.md with common development commands

**Conditional Execution**:
- **Skip if**: Project already has complete tooling (all config files exist AND pass validation)
- **Partial run if**: Some tooling exists but gaps identified
- **Full run if**: New project or missing critical tooling

**Output**:
- Configured linter (eslint/biome/clippy/ruff config)
- Configured formatter (prettier/biome/rustfmt/ruff config)
- Type checking setup (tsconfig strict/mypy/pyright config)
- Test framework setup (vitest/jest/pytest/cargo test config)
- Git hooks (husky/pre-commit config)
- Updated quickstart.md with setup instructions
- "Tech Debt" section in plan.md if issues found

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
