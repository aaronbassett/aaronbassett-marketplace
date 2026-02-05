---
description: Create or update the feature specification from a natural language feature description.
handoffs:
  - label: Build Technical Plan
    agent: sdd:plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: sdd:clarify
    prompt: Clarify specification requirements
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/sdd:specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

## Setup

Before executing this command, resolve the plugin root path for accessing templates and scripts:

```bash
# Invoke CPR resolver to create /tmp/cpr.py
Skill(skill="utils:find-claude-plugin-root")

# Then use it to resolve plugin paths
PLUGIN_ROOT=$(python3 /tmp/cpr.py sdd)
```

This creates the resolver script that all subsequent bash commands can use to find plugin resources.

## Execution

Given that feature description, do this:

1. **Generate a concise short name** (2-4 words) for the branch:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep it concise but descriptive enough to understand the feature at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Check for existing branches before creating new one**:

   a. First, fetch all remote branches to ensure we have the latest information:

      ```bash
      git fetch --all --prune
      ```

   b. Find the highest feature number across all sources for the short-name:
      - Remote branches: `git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
      - Local branches: `git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
      - Specs directories: Check for directories matching `specs/[0-9]+-<short-name>`

   c. Determine the next available number:
      - Extract all numbers from all three sources
      - Find the highest number N
      - Use N+1 for the new branch number

   d. Run the script from the plugin using the resolved PLUGIN_ROOT:
      - Get plugin root: `PLUGIN_ROOT=$(python3 /tmp/cpr.py sdd)`
      - Script path: `"$PLUGIN_ROOT"/skills/sdd-infrastructure/scripts/create-new-feature.sh`
      - Pass `--number N+1` and `--short-name "your-short-name"` along with the feature description
      - Bash example: `"$PLUGIN_ROOT"/skills/sdd-infrastructure/scripts/create-new-feature.sh --json --number 5 --short-name "user-auth" "Add user authentication"`
      - PowerShell example: `& "$PLUGIN_ROOT/skills/sdd-infrastructure/scripts/create-new-feature.sh" -Json -Number 5 -ShortName "user-auth" "Add user authentication"`

   **IMPORTANT**:
   - Check all three sources (remote branches, local branches, specs directories) to find the highest number
   - Only match branches/directories with the exact short-name pattern
   - If no existing branches/directories found with this short-name, start with number 1
   - You must only ever run this script once per feature
   - The JSON is provided in the terminal as output - always refer to it to get the actual content you're looking for
   - The JSON output will contain BRANCH_NAME and SPEC_FILE paths
   - For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot")

3. Load spec template to understand required sections:
   - First check for local override: `.sdd/templates/spec-template.md`
   - If not found, use plugin template: `"$PLUGIN_ROOT"/skills/sdd-infrastructure/templates/spec-template.md`

4. Follow this execution flow:

    1. Parse user description from Input
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **SOFT LIMIT: Try to keep to no more than 6 [NEEDS CLARIFICATION] markers total. It is better to breach this soft limit than to have ambiguous specs.**
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

6. **Codebase Mapping**: After writing spec.md, run codebase mapping to generate comprehensive project documentation:

   a. **Brownfield Detection**:

      Check if existing code exists in the repository:
      ```bash
      # Check for source files
      find . -name "*.ts" -o -name "*.tsx" -o -name "*.py" -o -name "*.rs" -o -name "*.go" | head -5
      ```

      ```bash
      # Check for package manifests
      ls package.json Cargo.toml pyproject.toml go.mod 2>/dev/null
      ```

      **If brownfield (existing code found)**:
      - Inform user: "Existing codebase detected. Running full codebase mapping..."
      - Invoke `/sdd:map full` to generate all 8 codebase documents
      - Documents will reflect current codebase state

      **If greenfield (no code found)**:
      - Inform user: "New project detected. Creating minimal codebase documents..."
      - Check `.sdd/memory/constitution.md` for tech preferences
      - If tech preferences exist, generate initial STACK.md with those preferences
      - Otherwise, use AskUserQuestion to ask about intended tech stack:
        - Present 2-3 recommended stacks based on spec requirements
        - Allow custom answer for modifications
      - Create minimal `.sdd/codebase/STACK.md` with intended tech stack
      - Other codebase documents will be populated after initial development

   b. **Update spec.md Reference**:
      - Add after the feature description: `**Codebase Documentation**: See [.sdd/codebase/](.sdd/codebase/) for technical details`

   c. **Codebase Documents Generated** (for brownfield):
      - `.sdd/codebase/STACK.md` - Languages, frameworks, dependencies
      - `.sdd/codebase/INTEGRATIONS.md` - External services, APIs
      - `.sdd/codebase/ARCHITECTURE.md` - System design, patterns
      - `.sdd/codebase/STRUCTURE.md` - Directory layout
      - `.sdd/codebase/CONVENTIONS.md` - Code style, naming
      - `.sdd/codebase/TESTING.md` - Test strategy, frameworks
      - `.sdd/codebase/SECURITY.md` - Auth, authorization
      - `.sdd/codebase/CONCERNS.md` - Tech debt, risks

7. **Common Elements Questions**: After codebase mapping, ask user about adding common requirements to spec:

   a. **Load Tech Context**:
      - Read `.sdd/codebase/STACK.md` to understand detected technologies
      - Read `.sdd/codebase/CONVENTIONS.md` for existing tooling
      - Read `.sdd/codebase/TESTING.md` for existing test setup

   b. **Always Ask** (via AskUserQuestion, multi-select format):

      Category: **Development Tools** (only if not already set up per CONVENTIONS.md)
      - Linting/formatting setup (tools based on detected stack)
        - TypeScript: ESLint + Prettier
        - Python: Ruff + Black
        - Rust: clippy + rustfmt
      - Pre-commit hooks
        - Node.js: husky
        - Python: pre-commit framework
        - Rust: git hooks with cargo fmt/clippy

   c. **Context-Dependent** (only ask if relevant):

      Use codebase documents and Glob to detect existing files/directories:

      - **If `justfile` exists**: "Add Justfile commands to spec?"
      - **If `.github/workflows/` exists**: "Add GitHub Workflows requirements to spec?"
      - **If git hooks**: "Enforce conventional commits?"
      - **If deployment mentioned in spec**: "Add Docker/containerization requirements?"
      - **If data model mentioned**: "Add database migration requirements?"
      - **If API mentioned**: "Add API documentation requirements (OpenAPI/Swagger)?"

      Category: **Version Control & Release**
      - Version management (semantic-release / cargo-release based on stack)
      - Changelog generation (conventional-changelog)

      Category: **Environment & Configuration**
      - Environment variable management (.env handling, validation)
      - Secrets management approach

      Category: **Testing & Quality** (only if not already set up per TESTING.md)
      - Testing framework setup (vitest/jest/pytest/cargo test based on stack)
      - Type checking configuration (TypeScript strict mode, mypy, etc.)
      - Code coverage requirements

   d. **Update spec.md with selected items**:
      - For each selected item, add appropriate requirement to relevant section
      - Development tools → Add to "Non-Functional Requirements" or new "Development Standards" section
      - Testing framework → Add to "Acceptance Criteria" or "Testing Requirements" section
      - Keep requirements technology-agnostic (focus on outcomes, not specific tools)

8. **Tech-Aware Specification Review**: Launch Task with appropriate dev agent to review spec:

   Based on detected tech stack from `.sdd/codebase/STACK.md`, invoke relevant agent:

   ```
   Task(
     subagent_type="[devs:typescript-dev|devs:python-dev|devs:rust-dev|devs:react-dev]",
     description="Review specification from tech perspective",
     prompt="Review this feature specification from the perspective of [technology] best practices.

             Spec: [spec.md content]
             Codebase Context:
             - STACK.md: [languages, frameworks, dependencies]
             - ARCHITECTURE.md: [system design, patterns]
             - CONVENTIONS.md: [code style, patterns]

             Check for:
             - Missing requirements specific to [technology] development
             - Unclear requirements that will be hard to implement in [technology]
             - Potential architecture issues given [technology] constraints
             - Missing non-functional requirements for [technology] apps

             Suggest improvements or additions (keep them technology-agnostic in phrasing)."
   )
   ```

   Incorporate agent feedback into spec before validation.

9. **Specification Quality Validation**: After tech-aware review, validate spec against quality criteria:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `FEATURE_DIR/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Notes

      - Items marked incomplete require spec updates before `/sdd:clarify` or `/sdd:plan`
      ```

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark checklist complete and proceed to step 6

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 6 markers exist, start with the 6 most critical (by scope/security/UX impact) then ask the user if they would like to clarify the rest or if you should make informed guesses
        3. For each clarification needed, present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status

10. Report completion with branch name, spec file path, codebase documents path, checklist results, and readiness for the next phase (`/sdd:clarify` or `/sdd:plan`).

    Include in report:
    - Branch name and number
    - Spec file path
    - Codebase documents path (`.sdd/codebase/`)
    - Documents generated (list 8 files if brownfield, or just STACK.md if greenfield)
    - Detected technologies (from STACK.md)
    - Common elements added to spec
    - Validation status
    - Next recommended command

**NOTE:** The script creates and checks out the new branch and initializes the spec file before writing.

## General Guidelines

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: RESTful APIs unless specified otherwise

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)
