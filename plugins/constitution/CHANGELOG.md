# Constitution Plugin Changelog

## [0.2.0] - 2026-01-25

### Added
- Plugin manifest for Claude Code marketplace discovery
- Checklist generator skill with semantic deduplication
- Amendment skill with semantic versioning (MAJOR/MINOR/PATCH)
- Constitution reviewer agent with severity-rated reports
- Prompt-based stop hooks for automated enforcement
- Integration between amendment and checklist generation
- Support for multiple review scopes (staged/diff/full/pr)
- Infinite loop prevention with stop_hook_active flag

### Changed
- Plugin now provides living governance system (not just write-once)
- Version tracking in constitution footer
- Changelog management (newest first)

### Technical Details
- 4 review modes: full, staged, diff, pr
- 3 severity levels: CRITICAL, MODERATE, MINOR
- Pattern detection for common violations
- Git-aware change detection
- Doc-only change allowance

## [0.1.0] - 2026-01-20

### Added
- Initial constitution writer skill
- Engineering principles reference
- Constitution template
- Support for different project types (hackathon, product, open source)

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) format.*
