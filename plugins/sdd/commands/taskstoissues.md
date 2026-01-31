---
description: Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Discover feature directory and validate prerequisites using Claude Code tools:

   a. **Find Feature Directory**:
      1. Use Bash to get current git branch: `git branch --show-current`
      2. Extract feature number prefix (e.g., "004" from "004-user-auth")
      3. Use Glob to find specs directory: `specs/{number}*/` where number matches prefix
      4. Store as FEATURE_DIR (absolute path)

   b. **Validate Required Files**:
      - Use Glob to verify `{FEATURE_DIR}/tasks.md` exists (REQUIRED)
        - If missing: ERROR "tasks.md not found. Run `/sdd:tasks` first."

   c. **Load tasks.md**:
      - Use Read to load `{FEATURE_DIR}/tasks.md` completely
      - Parse task structure to extract all tasks with their IDs, descriptions, and phases

2. Get the Git remote by running:

```bash
git config --get remote.origin.url
```

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

3. For each task in the list, use the GitHub CLI to create a new issue in the repository that is representative of the Git remote.

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL
