---
description: Create or update the project constitution through guided discovery (project characteristics → matched principles) or direct input, ensuring all dependent templates stay in sync. First-time users benefit from the interactive discovery workflow that recommends appropriate engineering principles based on project profile.
handoffs:
  - label: Build Specification
    agent: sdd:specify
    prompt: Implement the feature specification based on the updated constitution. I want to build...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Best Practices

**For first-time setup:**
- Let Phase 0 run the full discovery workflow
- This ensures principles are matched to your project's actual needs

**For updates:**
- Skip Phase 0 if you just want to amend specific principles
- Provide specific changes in $ARGUMENTS to go straight to Phase 1
- Phase 1 handles versioning, template sync, and validation automatically

**Recommendation:** Always run this command BEFORE `/sdd:specify` to establish project governance and quality gates that will inform all feature development.

## Setup

Before executing this command, resolve the plugin root path for accessing templates:

```bash
# Invoke CPR resolver to create /tmp/cpr.py
Skill(skill="bug-fixes:find-claude-plugin-root")

# Then use it to resolve plugin paths
PLUGIN_ROOT=$(python3 /tmp/cpr.py sdd)
```

## Outline

You are creating or updating the project constitution at `.sdd/memory/constitution.md`. The workflow has two phases:

**Phase 0: Constitution Generation** (if creating new or major revision)
- Discover project characteristics through structured questions
- Select appropriate principles from catalog based on project profile
- Generate tailored constitution content

**Phase 1: Constitution Template Update** (always)
- Load constitution template or generated content
- Fill placeholders with concrete values
- Version management and validation
- Propagate changes across dependent artifacts

Follow this execution flow:

### Phase 0: Constitution Generation (Conditional)

**When to run Phase 0:**
- Constitution file doesn't exist yet (first-time setup)
- User requests major constitutional revision ("start from scratch", "rebuild constitution")
- User provides minimal input and needs guidance ("create a constitution for my project")

**When to skip Phase 0:**
- Constitution exists and user provides specific principle updates
- User supplies complete constitution content in $ARGUMENTS
- Minor amendments or clarifications only

**If running Phase 0:**

0.1. **Tech Stack Detection** (BEFORE asking questions):
   - Use Glob to check if codebase documents exist: `.sdd/codebase/STACK.md`
   - If found: Use Read to load STACK.md for tech stack context
   - Extract tech stack information to inform Round 2 questions
   - Provide this context when calling the /constitution:writer skill

0.2. **Constitution Generator**
- Use the /constitution:writer skill
- Complete the /constitution:writer skill workflow with the user

0.3. **Proceed to Phase 1** - Continue with template update workflow below

### Phase 1: Constitution Template Update

1. Load the existing constitution template at `.sdd/memory/constitution.md`.
   - Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.
   **IMPORTANT**: The user might require less or more principles than the ones used in the template. If a number is specified, respect that - follow the general template. You will update the doc accordingly.

2. Collect/derive values for placeholders:
   - If you have user input, either from Phase 0 or via $ARGUMENTS, use it.
   - Otherwise infer from existing repo context (README, docs, prior constitution versions if embedded).
   - For governance dates: `RATIFICATION_DATE` is the original adoption date (if unknown ask or mark TODO), `LAST_AMENDED_DATE` is today if changes are made, otherwise keep previous.
   - `CONSTITUTION_VERSION` must increment according to semantic versioning rules:
     - MAJOR: Backward incompatible governance/principle removals or redefinitions.
     - MINOR: New principle/section added or materially expanded guidance.
     - PATCH: Clarifications, wording, typo fixes, non-semantic refinements.
   - If version bump type ambiguous, propose reasoning before finalizing.

3. Draft the updated constitution content:
   - Replace every placeholder with concrete text (no bracketed tokens left except intentionally retained template slots that the project has chosen not to define yet—explicitly justify any left).
   - Preserve heading hierarchy and comments can be removed once replaced unless they still add clarifying guidance.
   - Ensure each Principle section: succinct name line, paragraph (or bullet list) capturing non‑negotiable rules, explicit rationale if not obvious.
   - Ensure Governance section lists amendment procedure, versioning policy, and compliance review expectations.

4. Consistency propagation checklist (convert prior checklist into active validations):
   - Read `"$PLUGIN_ROOT"/skills/sdd-infrastructure/templates/plan-template.md` and ensure any "Constitution Check" or rules align with updated principles.
   - Read `"$PLUGIN_ROOT"/skills/sdd-infrastructure/templates/spec-template.md` for scope/requirements alignment—update if constitution adds/removes mandatory sections or constraints.
   - Read `"$PLUGIN_ROOT"/skills/sdd-infrastructure/templates/tasks-template.md` and ensure task categorization reflects new or removed principle-driven task types (e.g., observability, versioning, testing discipline).
   - Read each command file in `"$PLUGIN_ROOT"/skills/sdd-infrastructure/templates/commands/*.md` (including this one) to verify no outdated references (agent-specific names like CLAUDE only) remain when generic guidance is required.
   - Read any runtime guidance docs (e.g., `README.md`, `docs/quickstart.md`, or agent-specific guidance files if present). Update references to principles changed.

5. Produce a Sync Impact Report (prepend as an HTML comment at top of the constitution file after update):
   - Version change: old → new
   - List of modified principles (old title → new title if renamed)
   - Added sections
   - Removed sections
   - Templates requiring updates (✅ updated / ⚠ pending) with file paths
   - Follow-up TODOs if any placeholders intentionally deferred.

6. Validation before final output:
   - No remaining unexplained bracket tokens.
   - Version line matches report.
   - Dates ISO format YYYY-MM-DD.
   - Principles are declarative, testable, and free of vague language ("should" → replace with MUST/SHOULD rationale where appropriate).

7. Write the completed constitution back to `.sdd/memory/constitution.md` (overwrite).

8. Output a final summary to the user with:
   - **Phase 0 summary** (if Phase 0 was run):
     - Number of discovery questions asked and answered
     - Selected principles and why they match the project profile
     - Development standards included based on tech stack
   - **Phase 1 summary**:
     - New version and bump rationale
     - Any files flagged for manual follow-up
     - Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z (principle additions + governance update)` or `docs: create initial constitution v1.0.0`)
   - Next recommended command: `/sdd:specify` to create first feature using the constitution

Formatting & Style Requirements:

- Use Markdown headings exactly as in the template (do not demote/promote levels).
- Wrap long rationale lines to keep readability (<100 chars ideally) but do not hard enforce with awkward breaks.
- Keep a single blank line between sections.
- Avoid trailing whitespace.

If the user supplies partial updates (e.g., only one principle revision), still perform validation and version decision steps.

If critical info missing (e.g., ratification date truly unknown), insert `TODO(<FIELD_NAME>): explanation` and include in the Sync Impact Report under deferred items.

Do not create a new template; always operate on the existing `.sdd/memory/constitution.md` file.
