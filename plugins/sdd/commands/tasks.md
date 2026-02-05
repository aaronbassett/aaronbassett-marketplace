---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: sdd:analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: sdd:implement
    prompt: Start the implementation in phases
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Setup

Before executing this command, resolve the plugin root path for accessing templates:

```bash
# Invoke CPR resolver to create /tmp/cpr.py
Skill(skill="utils:find-claude-plugin-root")

# Then use it to resolve plugin paths
PLUGIN_ROOT=$(python3 /tmp/cpr.py sdd)
```

## Outline

1. **Setup**: Discover feature directory and available documents using Claude Code tools:

   a. **Find Feature Directory**:
      1. Use Bash to get current git branch: `git branch --show-current`
      2. Extract feature number prefix (e.g., "004" from "004-user-auth")
      3. Use Glob to find specs directory: `specs/{number}*/` where number matches prefix
      4. Store as FEATURE_DIR (absolute path)

   b. **Check for --drift Mode**:
      - If `$ARGUMENTS` contains `--drift`, enter Drift Update Mode (see section below)
      - Drift mode is triggered when codebase mapping detects structure changes

   c. **Check Required Files**:
      - Use Glob to verify `{FEATURE_DIR}/plan.md` exists (REQUIRED)
        - If missing: ERROR "plan.md not found. Run `/sdd:plan` first."
      - Use Glob to verify `{FEATURE_DIR}/spec.md` exists (REQUIRED)
        - If missing: ERROR "spec.md not found. Run `/sdd:specify` first."
      - Use Glob to check `.sdd/codebase/STACK.md` exists
        - If missing: WARN "Codebase documents not found. Run `/sdd:map` for full context."

   c. **Check Optional Documents** (use Glob for each):
      - `{FEATURE_DIR}/data-model.md` → Add to AVAILABLE_DOCS if exists
      - `{FEATURE_DIR}/contracts/*.{json,yaml,yml,md}` → Add "contracts/" if any found
      - `{FEATURE_DIR}/research.md` → Add to AVAILABLE_DOCS if exists
      - `{FEATURE_DIR}/quickstart.md` → Add to AVAILABLE_DOCS if exists

   d. **Validate Content** (semantic validation beyond file existence):
      - Use Read to load plan.md and check it has "Technical Context" or "Summary" section
        - If missing: ERROR "plan.md appears incomplete. Re-run `/sdd:plan`."
      - Use Read to load spec.md and check it has "User Scenarios" or "Functional Requirements"
        - If missing: ERROR "spec.md appears incomplete. Re-run `/sdd:specify`."

   **Result**: FEATURE_DIR and AVAILABLE_DOCS list ready for use

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (API endpoints), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map endpoints to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Generate tasks.md**: Use tasks template as structure (check `.sdd/templates/tasks-template.md` for local override, otherwise use `"$PLUGIN_ROOT"/skills/sdd-infrastructure/templates/tasks-template.md`), fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

Context for task generation: $ARGUMENTS

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action with exact file path

**Examples**:

- ✅ CORRECT: `- [ ] T001 Create project structure per implementation plan`
- ✅ CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- ✅ CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- ✅ CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- ❌ WRONG: `- [ ] Create User model` (missing ID and Story label)
- ❌ WRONG: `T001 [US1] Create model` (missing checkbox)
- ❌ WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- ❌ WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Endpoints/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**:
   - Map each contract/endpoint → to the user story it serves
   - If tests requested: Each contract → contract test task [P] before implementation in that story's phase

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup phase
   - Relationships → service layer tasks in appropriate story phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup phase (Phase 1)
   - Foundational/blocking tasks → Foundational phase (Phase 2)
   - Story-specific setup → within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
  - Project structure
  - Configuration files
  - Initial dependencies
  - **NO retro file for setup phase** (retros track implementation learnings)

- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
  - Shared infrastructure
  - Base models/services used across stories
  - **Start of Phase**: Create retro/P2.md from template
  - **End of Phase**: Run codebase mapping for Phase 2 changes (`/sdd:map incremental`)
  - **End of Phase**: Review retro/P2.md and extract critical learnings to CLAUDE.md (conservative)

- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - **Start of Each Phase**: Create retro/P{N}.md from template
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each phase should be a complete, independently testable increment
  - **End of Each Phase**: Run codebase mapping for Phase {N} changes (`/sdd:map incremental`)
  - **End of Each Phase**: Review retro/P{N}.md and extract critical learnings to CLAUDE.md (conservative)

- **Final Phase**: Polish & Cross-Cutting Concerns
  - **Start of Phase**: Create retro/P{final}.md from template
  - Cross-cutting refactoring
  - Performance optimization
  - Documentation
  - **End of Phase**: Run final codebase mapping (`/sdd:map incremental`)
  - **End of Phase**: Review retro/P{final}.md and extract critical learnings to CLAUDE.md (conservative)

### Drift Update Mode (`--drift`)

When structure drift is detected by `/sdd:map`, this mode updates only affected tasks:

1. **Detect Completed Tasks**:
   - Parse existing tasks.md for checkbox state: `- [x]` = done, `- [ ]` = pending
   - For each completed task, verify file exists at specified path
   - Build COMPLETED_TASKS list with task IDs

2. **Load Drift Report** (same as plan):
   - Which codebase documents changed
   - What specifically changed

3. **Map Drift to Task Categories**:

   | Change Type | Task Impact |
   |-------------|-------------|
   | New dependency | Add install task, may affect existing tasks |
   | Dir restructure | Update file paths in pending tasks |
   | Framework change | Regenerate implementation tasks, preserve completed |
   | Test strategy change | Regenerate test tasks if tests not yet written |
   | Security model change | Add security tasks, update auth-related tasks |

4. **Incremental Task Update Process**:
   - **Preserve**: All completed tasks (marked [x])
   - **Update paths**: For pending tasks affected by STRUCTURE changes
   - **Regenerate**: Only tasks in categories affected by drift
   - **Insert**: New tasks if new requirements detected
   - **Remove**: Tasks made obsolete by drift (with comment explaining why)

5. **Maintain Task ID Continuity**:
   - Completed tasks keep their IDs
   - New tasks get IDs after highest existing ID
   - Gap IDs from removed tasks are not reused

6. **Add Drift Update Section**:
   ```markdown
   ## Drift Updates

   ### {date}: Structure Drift (score: {N})

   **Changed**: {list of codebase docs that changed}

   **Tasks Preserved**: T001-T015 (completed)
   **Tasks Updated**: T016-T020 (path changes)
   **Tasks Regenerated**: T021-T030 (affected by framework change)
   **Tasks Removed**: T031-T033 (obsolete after restructure)
   **Tasks Added**: T034-T040 (new requirements from drift)
   ```

### Codebase Mapping Tasks

After each implementation phase (Foundational, User Stories, Polish), add a codebase mapping task:

**Purpose**: Keep codebase documentation accurate as implementation evolves

**Task Format**:
```text
- [ ] T### Run codebase mapping for Phase {N} changes (/sdd:map incremental)
```

**What Gets Updated**:
The incremental mapping will analyze changes and update relevant documents:
- STACK.md - New dependencies, version changes
- INTEGRATIONS.md - New external services
- ARCHITECTURE.md - Pattern changes, new components
- STRUCTURE.md - Directory changes
- CONVENTIONS.md - New patterns discovered
- TESTING.md - Test strategy updates
- SECURITY.md - Security changes
- CONCERNS.md - New tech debt or issues

**Example codebase mapping task**:
```text
- [ ] T035 [US1] Run codebase mapping for Phase 3 changes (/sdd:map incremental)
```

**Drift Detection**:
If the mapping detects significant structure changes (score >= 5), it will emit a STRUCTURE_DRIFT_ALERT.
If score >= 8, STRUCTURE_DRIFT_CRITICAL requires `/sdd:plan --drift && /sdd:tasks --drift`.

### Retrospective Documentation Tasks

For each implementation phase (Foundational and beyond), add retro creation and review tasks:

**Purpose**: Capture implementation learnings to build institutional knowledge and avoid repeating mistakes

**retro/P{N}.md Format**:
```markdown
# Phase {N} Retrospective: {Phase Name}

## What Worked Well
<!-- Effective patterns, tools, approaches -->

## What Didn't Work
<!-- Problems, issues, limitations encountered -->

## Workarounds & Solutions
<!-- Bug fixes, non-obvious solutions, clever workarounds -->

## Packages & Dependencies
<!-- Useful packages discovered, packages to avoid, version issues -->

## Patterns & Code
<!-- Reusable patterns, helpful code snippets, architectural insights -->

## For Next Time
<!-- Improvement suggestions, lessons learned, things to try differently -->
```

**Phase Start Task** (create retro file):
```text
- [ ] T### Create retro/P{N}.md for this phase
```

**Phase End Task** (review and extract critical learnings):
```text
- [ ] T### Review retro/P{N}.md and extract critical learnings to CLAUDE.md (conservative)
```

**CRITICAL Extraction Criteria** (be very conservative):
- Universal patterns applicable across entire project (not phase-specific)
- Critical bug workarounds affecting other features (not temporary solutions)
- Major architectural decisions with lasting impact (not minor discoveries)
- **NOT**: Phase-specific details, temporary solutions, minor package finds

**Example retro tasks for Phase 3**:
```text
- [ ] T020 [US1] Create retro/P3.md for this phase
... (implementation tasks) ...
- [ ] T036 [US1] Review retro/P3.md and extract critical learnings to CLAUDE.md (conservative)
```

**Benefits**:
- Captures fresh knowledge while implementation details are in working memory
- Builds project-wide learning that informs future planning (via sdd:plan retro review)
- Avoids repeating mistakes across features
- Creates institutional knowledge independent of team member availability

### Agent References in Task Descriptions

**Purpose**: Guide task execution to use appropriate tech-specific custom agents for better implementation quality

When generating task descriptions, detect the technology from `.sdd/codebase/STACK.md` and reference appropriate agents:

**Agent Detection Rules**:
- `.ts` or `.tsx` files → Reference `devs:typescript-dev` agent
- `.rs` files → Reference `devs:rust-dev` agent
- `.py` files → Reference `devs:python-dev` agent
  - If FastAPI detected in STACK.md → Also mention `devs:python-dev` context
- `.jsx` files → Reference `devs:react-dev` agent
- Next.js context (app/, pages/, next.config in file paths) → Also reference `devs:react-dev` agent
- Tauri context (src-tauri/ in file paths) → Also reference `devs:rust-dev` agent
- Generic config/setup tasks → Reference init-local-tooling skill rather than an agent

**Task Description Format with Agent Reference**:
```text
- [ ] T### [P?] [Story?] {Action} in {file_path} (use {agent-name} agent)
```

**Examples**:

TypeScript task:
```text
- [ ] T012 [P] [US1] Implement User model in src/models/user.ts (use devs:typescript-dev agent)
```

Python/FastAPI task:
```text
- [ ] T018 [US1] Create authentication endpoint in src/api/auth.py (use devs:python-dev agent)
```

Next.js task:
```text
- [ ] T024 [P] [US2] Implement dashboard page in app/dashboard/page.tsx (use devs:react-dev agent)
```

Rust task:
```text
- [ ] T030 [P] [US3] Implement data processor in src/processor.rs (use devs:rust-dev agent)
```

Config task (no specific agent):
```text
- [ ] T003 Configure ESLint and Prettier per STACK.md (use init-local-tooling skill)
```

**Benefits**:
- Explicit agent routing during implementation (sdd:implement can parse agent from task)
- Consistent use of tech-specific best practices
- Better code quality through specialized agent expertise
- Clear execution guidance for each task

### Git Workflow (REQUIRED)

**Purpose**: Enforce a standard GitHub workflow to ensure clean version control, passing CI, and proper code review gates.

Every generated tasks.md MUST include git workflow tasks at phase boundaries. The workflow ensures isolated feature development, atomic commits, and proper PR-based integration.

#### Phase Start Tasks (REQUIRED for each phase)

Before any implementation work begins in a phase, generate these git workflow tasks:

**First Phase Only** (Phase 1 or first implementation phase):
```text
- [ ] T001 [GIT] Verify on main branch and working tree is clean
- [ ] T002 [GIT] Pull latest changes from origin/main
- [ ] T003 [GIT] Create feature branch: {feature-number}-{feature-name}
```

**Subsequent Phases** (if continuing on same branch):
```text
- [ ] T### [GIT] Verify working tree is clean before starting Phase {N}
- [ ] T### [GIT] Pull and rebase on origin/main if needed
```

**Git Verification Steps** (for T001-style tasks):
1. Run `git branch --show-current` - must be `main` (or configured default branch)
2. Run `git status --porcelain` - must be empty (clean working tree)
3. If not clean: ERROR "Working tree has uncommitted changes. Commit or stash before proceeding."
4. If not on main: ERROR "Not on main branch. Switch to main before starting new feature."

**Pull/Sync Steps** (for T002-style tasks):
1. Run `git fetch origin`
2. Run `git merge origin/main` (or `git rebase origin/main` based on project preference)
3. If conflicts: ERROR "Merge conflicts detected. Resolve before proceeding."

**Branch Creation Steps** (for T003-style tasks):
1. Extract feature number from spec (e.g., "004" from "004-user-auth")
2. Create branch: `git checkout -b {number}-{feature-slug}`
3. Example: `git checkout -b 004-user-authentication`

#### After-Task Commits (REQUIRED)

After EVERY implementation task, generate a commit task:

**Task Format**:
```text
- [ ] T### [GIT] Commit: {brief description of previous task}
```

**Commit Execution Steps**:
1. Run `git add -A` (or specific files from previous task)
2. Run `git commit -m "{conventional commit message}"`
3. **Pre-commit hooks MUST pass** - if hooks fail:
   - Fix the issues identified by hooks (linting, formatting, type errors)
   - Re-stage fixed files
   - Retry commit
   - Do NOT use `--no-verify` to skip hooks
4. Commit message format: `{type}({scope}): {description}`
   - Types: feat, fix, docs, style, refactor, test, chore
   - Scope: component or area affected
   - Example: `feat(auth): implement user login endpoint`

**Example commit tasks in context**:
```text
- [ ] T012 [P] [US1] Create User model in src/models/user.ts (use devs:typescript-dev agent)
- [ ] T013 [GIT] Commit: add User model
- [ ] T014 [US1] Implement UserService in src/services/user_service.ts (use devs:typescript-dev agent)
- [ ] T015 [GIT] Commit: add UserService with CRUD operations
```

**Batching Exception**: For small, related tasks that are parallelizable [P], commits may be batched:
```text
- [ ] T020 [P] [US1] Create LoginForm component in src/components/LoginForm.tsx
- [ ] T021 [P] [US1] Create RegisterForm component in src/components/RegisterForm.tsx
- [ ] T022 [GIT] Commit: add authentication form components
```

#### Phase End Tasks (REQUIRED)

At the end of EVERY phase (including Setup, Foundational, each User Story, and Polish), generate these completion tasks:

**Phase Completion Block**:
```text
- [ ] T### [GIT] Push branch to origin (ensure pre-push hooks pass)
- [ ] T### [GIT] Create/update PR to main with phase summary
- [ ] T### [GIT] Verify all CI checks pass
- [ ] T### [GIT] Report PR ready status
```

**Push Execution Steps** (for push task):
1. Run `git push -u origin {branch-name}` (first push) or `git push` (subsequent)
2. **Pre-push hooks MUST pass** - if hooks fail:
   - Fix identified issues (tests, build, lint)
   - Commit fixes
   - Retry push
   - Do NOT use `--no-verify` to skip hooks
3. If push rejected due to remote changes:
   - Pull and rebase/merge
   - Resolve any conflicts
   - Push again

**PR Creation Steps** (for PR task):
1. Check if PR already exists for this branch: `gh pr list --head {branch-name}`
2. If no PR exists, create one:
   ```bash
   gh pr create --title "{feature-name}: Phase {N} complete" \
     --body "## Summary\n{phase summary}\n\n## Changes\n{list of changes}\n\n## Testing\n{test instructions}"
   ```
3. If PR exists, update body with phase progress:
   ```bash
   gh pr edit {pr-number} --body "{updated body with phase status}"
   ```

**CI Verification Steps** (for CI check task):
1. Run `gh pr checks {pr-number}` to view CI status
2. If any checks are pending: Wait and re-check
3. If any checks fail:
   - Identify failing check from output
   - Fix the issue locally
   - Commit the fix
   - Push to trigger new CI run
   - Repeat until all checks pass
4. Do NOT proceed until ALL checks are green

**PR Ready Report** (for report task):

Once ALL CI checks pass, output EXACTLY this format:

```text
**PR #{pr-number} READY FOR MERGE. AWAITING LGTM**

{pr-url}
```

**CRITICAL**: After outputting this message, STOP. Do not continue to the next phase or perform any additional work. The feature/phase is complete and awaiting human review.

**Example**:
```text
**PR #42 READY FOR MERGE. AWAITING LGTM**

https://github.com/owner/repo/pull/42
```

#### Complete Phase Example

Here's how git workflow tasks integrate into a complete phase:

```text
## Phase 3: User Authentication [US1]

### Phase Start
- [ ] T020 [GIT] Verify working tree is clean before starting Phase 3
- [ ] T021 [GIT] Pull and rebase on origin/main if needed

### Implementation
- [ ] T022 [US1] Create retro/P3.md for this phase
- [ ] T023 [GIT] Commit: initialize phase 3 retro
- [ ] T024 [P] [US1] Create User model in src/models/user.ts (use devs:typescript-dev agent)
- [ ] T025 [P] [US1] Create AuthService in src/services/auth.ts (use devs:typescript-dev agent)
- [ ] T026 [GIT] Commit: add User model and AuthService
- [ ] T027 [US1] Implement login endpoint in src/api/auth.ts (use devs:typescript-dev agent)
- [ ] T028 [GIT] Commit: implement login endpoint
- [ ] T029 [US1] Implement logout endpoint in src/api/auth.ts (use devs:typescript-dev agent)
- [ ] T030 [GIT] Commit: implement logout endpoint
- [ ] T031 [US1] Run /sdd:map incremental for Phase 3 changes
- [ ] T032 [GIT] Commit: update codebase documents for phase 3
- [ ] T033 [US1] Review retro/P3.md and extract critical learnings to CLAUDE.md (conservative)
- [ ] T034 [GIT] Commit: finalize phase 3 retro

### Phase Completion
- [ ] T035 [GIT] Push branch to origin (ensure pre-push hooks pass)
- [ ] T036 [GIT] Create/update PR to main with phase summary
- [ ] T037 [GIT] Verify all CI checks pass
- [ ] T038 [GIT] Report PR ready status
```

#### Workflow Rules Summary

| Trigger | Required Action | Failure Handling |
|---------|-----------------|------------------|
| Phase start | Clean tree, on main (first phase), pull latest | ERROR and stop |
| First phase | Create feature branch | ERROR if branch exists |
| After each task | Commit with hooks | Fix issues, retry |
| Phase end | Push with hooks | Fix issues, retry |
| After push | Create/update PR | Retry on failure |
| After PR | Wait for CI green | Fix failures, re-push |
| CI passes | Output ready message | STOP and wait for LGTM |

**Benefits**:
- Atomic commits make review and rollback easier
- Pre-commit hooks catch issues early
- CI verification ensures quality gates are met
- Clear stopping point prevents premature merge
- PR-based workflow enables proper code review
