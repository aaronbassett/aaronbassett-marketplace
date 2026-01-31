---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/sdd:tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The project constitution (`.sdd/memory/constitution.md`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle. If a principle itself needs to change, that must occur in a separate, explicit constitution update outside `/sdd:analyze`.

## Execution Steps

### 1. Initialize Analysis Context

Discover feature directory and validate all required artifacts using Claude Code tools:

a. **Find Feature Directory**:
   1. Use Bash to get current git branch: `git branch --show-current`
   2. Extract feature number prefix (e.g., "004" from "004-user-auth")
   3. Use Glob to find specs directory: `specs/{number}*/` where number matches prefix
   4. Store as FEATURE_DIR (absolute path)

b. **Validate Required Artifacts** (All REQUIRED for analysis):
   - Use Glob to verify `{FEATURE_DIR}/tasks.md` exists
     - If missing: ERROR "tasks.md not found. Run `/sdd:tasks` first."
   - Use Glob to verify `{FEATURE_DIR}/plan.md` exists
     - If missing: ERROR "plan.md not found. Run `/sdd:plan` first."
   - Use Glob to verify `{FEATURE_DIR}/spec.md` exists
     - If missing: ERROR "spec.md not found. Run `/sdd:specify` first."

c. **Check Optional Supporting Documents**:
   - Use Glob to check `.sdd/codebase/STACK.md` → Add to AVAILABLE_DOCS if exists
   - Use Glob to check for other codebase documents in `.sdd/codebase/`:
     - CONVENTIONS.md, TESTING.md, SECURITY.md, ARCHITECTURE.md, STRUCTURE.md, INTEGRATIONS.md, CONCERNS.md
   - Use Glob to check `{FEATURE_DIR}/data-model.md` → Add to AVAILABLE_DOCS if exists
   - Use Glob to check `{FEATURE_DIR}/contracts/` → Add if any files found
   - Use Glob to check `{FEATURE_DIR}/research.md` → Add to AVAILABLE_DOCS if exists

d. **Semantic Validation** (beyond file existence):
   - Use Read to load tasks.md and verify:
     - Has phase headers (Phase 1, Phase 2, etc.)
     - Has tasks in checkbox format `- [ ] [ID]`
     - If malformed: ERROR "tasks.md appears incomplete. Re-run `/sdd:tasks`."
   - Use Read to load plan.md and verify:
     - Has "Summary" or "Technical Context" section
     - References stack or technical decisions
     - If missing: ERROR "plan.md appears incomplete. Re-run `/sdd:plan`."
   - Use Read to load spec.md and verify:
     - Has "Functional Requirements" or "User Scenarios" section
     - Has "Success Criteria" section
     - If missing: ERROR "spec.md appears incomplete. Re-run `/sdd:specify`."

e. **Derive Absolute Paths**:
   - SPEC = `{FEATURE_DIR}/spec.md`
   - PLAN = `{FEATURE_DIR}/plan.md`
   - TASKS = `{FEATURE_DIR}/tasks.md`
   - CODEBASE_DOCS = `.sdd/codebase/` (if exists)

**Benefits over bash script**:
- Semantic validation of artifact completeness
- Checks for proper structure, not just file existence
- Includes codebase documents in analysis if available
- Can detect partially-completed artifacts and provide specific guidance

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From plan.md:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**

- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths

**From constitution:**

- Load `.sdd/memory/constitution.md` for principle validation

### 2.5. Parallel Artifact Analysis (PERFORMANCE OPTIMIZATION)

Instead of sequential analysis, launch 3 Explore agents in parallel (single message, multiple Task calls) to analyze different aspects:

**Agent 1 - Spec Completeness & Consistency**:
```
Task(
  subagent_type="Explore",
  description="Analyze spec completeness",
  prompt="Analyze spec.md for completeness and consistency.

          Focus on:
          - Are all functional requirements testable and unambiguous?
          - Are success criteria measurable and technology-agnostic?
          - Are user scenarios complete with acceptance criteria?
          - Are edge cases identified and specified?
          - Any vague adjectives lacking measurable criteria?
          - Any unresolved placeholders or [NEEDS CLARIFICATION] markers?
          - Terminology consistency within spec

          Return findings in structured format:
          - Issue type (Ambiguity, Underspecification, Inconsistency)
          - Location (section, line reference if possible)
          - Severity (CRITICAL, HIGH, MEDIUM, LOW)
          - Description
          - Recommendation"
)
```

**Agent 2 - Plan Feasibility & Alignment**:
```
Task(
  subagent_type="Explore",
  description="Analyze plan feasibility",
  prompt="Analyze plan.md for technical feasibility and alignment with spec.md and codebase documents.

          Focus on:
          - Does plan align with spec requirements?
          - Are technical decisions justified and documented?
          - Does plan reference tech stack from STACK.md correctly?
          - Are data entities consistent with spec?
          - Are dependencies and constraints addressed?
          - Any conflicting technical decisions?
          - Missing implementation details for complex requirements?

          Return findings in structured format:
          - Issue type (Inconsistency, Missing Detail, Conflict)
          - Location (section, related spec requirement)
          - Severity
          - Description
          - Recommendation"
)
```

**Agent 3 - Tasks Coverage & Dependencies**:
```
Task(
  subagent_type="Explore",
  description="Analyze task coverage",
  prompt="Analyze tasks.md for coverage and proper dependency ordering.

          Focus on:
          - Do all spec requirements have corresponding tasks?
          - Do all tasks map to spec requirements or plan elements?
          - Are tasks properly ordered with dependencies respected?
          - Are parallel opportunities marked correctly [P]?
          - Do tech-specific tasks reference appropriate agents?
          - Are codebase mapping tasks included per phase?
          - Are retro creation/review tasks included?
          - Any orphan tasks with no requirement mapping?

          Return findings in structured format:
          - Issue type (Coverage Gap, Dependency Issue, Ordering Problem)
          - Location (task ID, requirement ID)
          - Severity
          - Description
          - Recommendation"
)
```

Wait for all three agents to complete, then consolidate findings for the next step.

**Benefits**:
- 3x faster analysis (parallel execution)
- Each agent specializes in one artifact
- Better coverage through focused analysis
- Structured findings ready for reporting

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Non-functional requirements not reflected in tasks (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Data entities referenced in plan but absent in spec (or vice versa)
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/sdd:implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /sdd:specify with refinement", "Run /sdd:plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Skill-Based Remediation

**Purpose**: Provide intelligent, tech-aware remediation suggestions for identified issues

**Process**:

1. **Ask User**: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically)

2. **If User Approves, Generate Tech-Specific Remediation**:

   a. **Load Tech Stack Context**:
      - Use Read to load `.sdd/codebase/STACK.md` (if exists) to understand tech stack
      - Identify which skills are relevant (typescript-core, python-core, rust-core, react-core, security-core)

   b. **For Each High/Critical Issue**, Generate Remediation:

      **Inconsistency Issues**:
      - Launch Task with Plan agent:
        - Prompt: "Suggest remediation for this consistency issue: [issue description]
                   Context: Tech stack is [detected stack from STACK.md]
                   Affected files/sections: [locations from issue]
                   Provide specific edit suggestions with before/after examples"
      - If tech-specific: Reference relevant skill in remediation
        - Example: "Update spec.md to align with python-core for endpoint documentation:
                   - Before: 'API should be fast'
                   - After: 'API endpoints should respond within 200ms for 95th percentile requests'"

      **Coverage Gap Issues**:
      - Reference skills for tech-specific requirements:
        - TypeScript gaps: "According to typescript-core, add requirements for:
                           - Type safety at API boundaries
                           - Error handling with typed exceptions"
        - Python/FastAPI gaps: "According to python-core, add requirements for:
                        - Request/response validation schemas
                        - Async endpoint specifications"
        - React/Next.js gaps: "According to react-core, add requirements for:
                        - Data fetching strategy (SSR/SSG/ISR)
                        - Image optimization specifications"

      **Ambiguity Issues**:
      - Provide concrete, measurable alternatives:
        - If Performance ambiguity + Next.js: Reference react-core
          - "Replace 'fast loading' with: 'Initial page load completes in <1.5s (Lighthouse score)'"
        - If API ambiguity + FastAPI: Reference python-core
          - "Replace 'robust error handling' with: 'All endpoints return OpenAPI-compliant error responses with status code, message, and optional details field'"

      **Constitution Violations**:
      - Reference constitution principles directly
      - If tech-specific violation: Reference appropriate skill
        - Example: "Constitution requires comprehensive error handling. Per python-core:
                   - Add requirements for exception hierarchy
                   - Specify logging requirements for all error paths"

   c. **Format Remediation Suggestions**:

      ```markdown
      ## Remediation Plan

      ### Issue A1: [Issue Summary]
      **Location**: spec.md:L120-134
      **Severity**: HIGH
      **Type**: Duplication

      **Suggested Fix**:
      1. Remove duplicate requirement at spec.md:L127-130
      2. Consolidate into single requirement at L120:
         ```
         [Specific requirement text that combines both]
         ```
      3. Update related acceptance criteria in section §4.2

      **Tech-Specific Guidance** (from [skill-name]):
      - [Skill-based recommendation]
      ```

   d. **Prioritize Remediation**:
      - Start with CRITICAL issues (constitution violations)
      - Then HIGH issues (blocking inconsistencies, missing core coverage)
      - Group related issues (e.g., all ambiguities in NFR section)
      - Limit to top 10 issues to avoid overwhelming user

   e. **Present Remediation Options**:
      - Show remediation plan as markdown output
      - Ask: "Would you like me to apply these changes? (yes/no/selective)"
      - If "selective": Allow user to approve individual fixes
      - If "yes": Apply all fixes using Edit tool
      - If "no": Save remediation plan to FEATURE_DIR/analysis-remediation.md for reference

**Benefits of Skill-Based Remediation**:
- Context-aware fixes aligned with tech stack best practices
- Specific, actionable suggestions (not generic advice)
- References authoritative skills for quality standards
- Reduces iteration cycles between analysis and fixing
- Maintains consistency with project's custom standards

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)

## Context

$ARGUMENTS
