---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Discover feature directory, validate prerequisites, and load task list using Claude Code tools:

   a. **Find Feature Directory**:
      1. Use Bash to get current git branch: `git branch --show-current`
      2. Extract feature number prefix (e.g., "004" from "004-user-auth")
      3. Use Glob to find specs directory: `specs/{number}*/` where number matches prefix
      4. Store as FEATURE_DIR (absolute path)

   b. **Check Required Files** (Implementation Phase Requirements):
      - Use Glob to verify `{FEATURE_DIR}/tasks.md` exists (REQUIRED for implementation)
        - If missing: ERROR "tasks.md not found. Run `/sdd:tasks` first."
      - Use Glob to verify `{FEATURE_DIR}/plan.md` exists (REQUIRED)
        - If missing: ERROR "plan.md not found. Run `/sdd:plan` first."
      - Use Glob to verify `{FEATURE_DIR}/spec.md` exists (REQUIRED)
        - If missing: ERROR "spec.md not found. Run `/sdd:specify` first."
      - Use Glob to check `.sdd/codebase/STACK.md` exists
        - If missing: WARN "Codebase documents not found. Run `/sdd:map` first for full context."
      - Use Glob to check for other codebase documents in `.sdd/codebase/`:
        - CONVENTIONS.md, TESTING.md, SECURITY.md, ARCHITECTURE.md, STRUCTURE.md, INTEGRATIONS.md, CONCERNS.md

   c. **Load and Validate tasks.md** (include task content for execution):
      - Use Read to load `{FEATURE_DIR}/tasks.md` completely
      - Parse task structure:
        - Extract phases (Setup, Foundational, User Stories, Polish)
        - Extract tasks with format: `- [ ] [ID] [P?] [Story?] Description`
        - Build task list with: task_id, parallel_flag, story_label, description, file_paths, status
      - Validate task file structure:
        - Check it has "Phase 1: Setup" or similar phase headers
        - Check tasks follow checkbox format
        - If malformed: ERROR "tasks.md appears invalid. Re-run `/sdd:tasks`."
      - Store as TASKS list for execution

   d. **Check Optional Documents** (use Glob for each):
      - `{FEATURE_DIR}/data-model.md` → Add to AVAILABLE_DOCS if exists
      - `{FEATURE_DIR}/contracts/*.{json,yaml,yml,md}` → Add "contracts/" if any found
      - `{FEATURE_DIR}/research.md` → Add to AVAILABLE_DOCS if exists
      - `{FEATURE_DIR}/quickstart.md` → Add to AVAILABLE_DOCS if exists
      - `{FEATURE_DIR}/retro/*.md` → Check if retro directory exists (for phase continuity)

   e. **Validate Content** (semantic validation):
      - Use Read to load plan.md and check for "Technical Context" or stack information
        - If missing: ERROR "plan.md appears incomplete. Re-run `/sdd:plan`."
      - Use Read to load spec.md and check for "User Scenarios" or "Functional Requirements"
        - If missing: ERROR "spec.md appears incomplete. Re-run `/sdd:specify`."

   **Result**: FEATURE_DIR, AVAILABLE_DOCS list, and TASKS ready for execution

2. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

3. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

   **Load Codebase Documents** (from `.sdd/codebase/`):
   - **REQUIRED**: Read STACK.md for languages, frameworks, dependencies
   - **REQUIRED**: Read CONVENTIONS.md for code style and patterns
   - **IF EXISTS**: Read TESTING.md for test strategy and frameworks
   - **IF EXISTS**: Read SECURITY.md for auth and security patterns
   - **IF EXISTS**: Read ARCHITECTURE.md for system design context
   - **IF EXISTS**: Read STRUCTURE.md for directory layout guidance
   - **IF EXISTS**: Read INTEGRATIONS.md for external service context
   - **IF EXISTS**: Read CONCERNS.md for known issues and tech debt

4. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Check if the following command succeeds to determine if the repository is a git repo (create/verify .gitignore if so):

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - Check if Dockerfile* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc* exists → create/verify .eslintignore
   - Check if eslint.config.* exists → ensure the config's `ignores` entries cover required patterns
   - Check if .prettierrc* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

6. **Tech-Specific Task Execution with Retro Capture**: Execute tasks using appropriate custom agents and capture learnings:

   a. **Phase Start**:
      - Check if `{FEATURE_DIR}/retro/P{phase_number}.md` exists
      - If not, create it from retro template structure (see format below)
      - Mark "Create retro file" task as [X] in tasks.md

   b. **For Each Task** in current phase:

      1. **Detect Appropriate Agent** from task description and file paths:
         - `.ts` or `.tsx` files → `devs:typescript-dev`
         - `.rs` files → `devs:rust-dev`
         - `.py` files → `devs:python-dev`
         - `.jsx` files → `devs:react-dev`
         - Next.js context (app/, pages/, next.config) → `devs:react-dev`
         - Tauri context (src-tauri/) → `devs:rust-dev`
         - Generic/config tasks → Use init-local-tooling skill

      2. **Read Relevant Context** for agent:
         - `.sdd/codebase/STACK.md` (tech stack and decisions)
         - `.sdd/codebase/CONVENTIONS.md` (code style and patterns)
         - `.sdd/codebase/TESTING.md` (test frameworks and patterns)
         - `.sdd/codebase/SECURITY.md` (auth and security patterns)
         - plan.md section for this phase
         - data-model.md if task involves entities
         - contracts/ if task involves API endpoints
         - Previous retro files for relevant learnings

      3. **Launch Task Agent** with comprehensive context:

         ```
         Task(
           subagent_type="[detected-agent]",
           description="[task description from tasks.md]",
           prompt="[Task Description]

                   Context:
                   - Tech Stack (from STACK.md): [relevant technologies]
                   - Conventions (from CONVENTIONS.md): [code style, patterns]
                   - Testing (from TESTING.md): [test frameworks, patterns]
                   - Security (from SECURITY.md): [auth patterns if relevant]
                   - Plan Details: [architecture/structure for this component]
                   - Data Model: [entities/relationships if relevant]
                   - Best Practices: Follow [technology]-core skill

                   After implementation, report:
                   1. **Codebase changes**: List any technologies added/removed/updated
                      - New dependencies installed
                      - Version changes
                      - Tool additions
                      - Pattern changes
                   2. **Retro items** (be specific):
                      - What Worked Well: [effective patterns, helpful tools]
                      - What Didn't Work: [issues encountered, limitations]
                      - Workarounds & Solutions: [how problems were solved]
                      - Packages & Dependencies: [useful finds, packages to avoid]
                      - Patterns & Code: [reusable patterns discovered]
                      - For Next Time: [improvements for future phases]"
         )
         ```

      4. **Process Agent Response**:
         - If agent reports codebase changes (dependencies, tools, patterns):
           - Note changes for incremental codebase mapping at phase end
         - If agent reports retro items:
           - Use Edit to append to appropriate section in `{FEATURE_DIR}/retro/P{phase_number}.md`
         - Use Edit to mark task as [X] in tasks.md

      5. **Parallel Task Handling**:
         - Group [P] tasks by tech stack
         - Launch multiple agents in parallel (single message, multiple Task calls)
         - Process all responses before continuing

   c. **Phase End**:
      - When "Review retro and extract critical learnings" task is reached:
        1. Use Read to load `{FEATURE_DIR}/retro/P{phase_number}.md`
        2. Identify **CRITICAL** learnings (be very conservative):
           - Universal patterns applicable across entire project
           - Critical bug workarounds affecting other features
           - Major architectural decisions with lasting impact
           - **NOT**: Phase-specific details, temporary solutions, minor discoveries
        3. If critical learnings found:
           - Use Read to load CLAUDE.md
           - Use Edit to add to CLAUDE.md under appropriate section
           - Add concise entry with context (which phase, what problem, what solution)
        4. Mark task as [X] in tasks.md

   d. **Incremental Codebase Mapping** (at end of each phase):
      - Run `/sdd:map incremental` to update codebase documents with phase changes
      - The mapper will analyze changes made during the phase and update:
        - STACK.md (new dependencies, version changes)
        - CONVENTIONS.md (new patterns discovered)
        - TESTING.md (new test patterns)
        - CONCERNS.md (new tech debt identified)

   e. **Structure Drift Detection**:
      - After codebase mapping, check for STRUCTURE_DRIFT_ALERT in output
      - **If STRUCTURE_DRIFT_ALERT (score >= 5)**:
        - Display warning: "Structure drift detected. Consider running `/sdd:plan --drift`."
        - Continue with implementation unless user requests pause
      - **If STRUCTURE_DRIFT_CRITICAL (score >= 8)**:
        - **PAUSE** implementation
        - Display: "Critical structure drift detected. Recommend running:"
          - `/sdd:plan --drift` to update plan
          - `/sdd:tasks --drift` to update tasks
        - Ask user: "Proceed with implementation or pause to update plan/tasks?"
        - Wait for user response before continuing

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

7. **Implementation Execution Rules**:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] grouped by tech
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: After each phase, validate with relevant -core skills

8. **Progress Tracking and Error Handling**:
   - Report progress after each completed task
   - Show codebase document updates and retro updates as they happen
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT**: Always mark completed tasks as [X] in tasks.md immediately

9. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/sdd:tasks` first to regenerate the task list.
