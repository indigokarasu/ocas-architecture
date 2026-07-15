# spec-ocas-skill-publishing.md

Version: 1.1.0
Author: Indigo Karasu

---

## Purpose

This spec defines the structure and format for every OCAS skill package's publishing artifacts: `README.md`, `CHANGELOG.md`, GitHub releases, and version numbering. Every skill repository must follow this spec so that README and CHANGELOG stay consistent across edits, authors, and time.

**Related specs:** `ocas-skill-authoring-rules.md` governs SKILL.md content. This spec governs everything else in the repo that faces the outside world.

---

## README.md

Every skill repository must have a `README.md` at the repo root. It is the public-facing summary of the skill package. It is **not** a substitute for SKILL.md — it is a navigation aid and quick reference for humans browsing GitHub.

### Required sections, in order

```
# [emoji] [Skill Name]

[One-sentence description — same core content as the SKILL.md description field]

Skill packages follow the [agentskills.io](https://agentskills.io/specification) open standard
and are compatible with OpenClaw, Hermes Agent, and any agentskills.io-compliant client.

---

## Overview

## Commands

## Setup

## Dependencies

## Scheduled Tasks

## Changelog
```

### Section rules

**Header (`# [emoji] [Skill Name]`)**
- Use a single emoji that reflects the skill's domain
- Skill name is the human-readable name (e.g. `Scout`, not `ocas-scout`)
- Followed immediately by the one-sentence description (no blank line between emoji header and description)

**Overview**
- 2–4 sentences describing what the skill does and its key behaviors
- Do not repeat the one-sentence header description verbatim — expand it
- End with one sentence on what the skill emits or cooperates with, if relevant

**Commands**
- Markdown table: `| Command | Description |`
- Every command listed in SKILL.md `## Commands` must appear here
- Description is a single concise phrase — do not paste the full SKILL.md command description

**Setup**
- One short paragraph describing what `{skill}.init` does automatically
- If no manual setup is required, say so explicitly
- If any optional credentials or binaries are needed, list them here (one line each)
- If the skill reads behavioral config from `config.yaml` (`skills.config.<key>`), state that here and point to the SKILL.md Configuration section. Do **not** instruct users to set environment variables for non-secret tuning — that is a submission-blocking anti-pattern (see `spec-ocas-scripts.md` → Configuration).

**Configuration** (required when the skill has any `metadata.hermes.config` keys)
- Markdown table: `| Config key (`skills.config.<key>`) | Default | Description |`
- One row per declared key, sourced from `metadata.hermes.config`
- Never document env-var names (`GENIE_*`, `<NAME>_*`) as the user-facing control

**Dependencies**
- Two subsections: `**OCAS Skills**` and `**External**`
- OCAS Skills: link to each cooperative skill's GitHub repo with a one-phrase role
- External: tools, APIs, binaries used; mark each `(optional)` or `(required)`
- Omit subsection entirely if empty (no external deps, or no OCAS skill deps)

**Scheduled Tasks**
- Table: `| Job | Mechanism | Schedule | Command |`
- Same content as the `## Background tasks` table in SKILL.md
- Omit section entirely if the skill has no background tasks

**Changelog**
- Most recent version entry at top
- Format per entry:
  ```
  ### vX.Y.Z — Month DD, YYYY
  - [bullet summary of change]
  - [bullet summary of change]
  ```
- Keep the last 3–5 entries in the README. Older history lives in CHANGELOG.md only.
- Never paste the full CHANGELOG into the README

---

## CHANGELOG.md

Every skill repository must have a `CHANGELOG.md` at the repo root. It is the append-only history of every version. Most recent entry at top.

### Format

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New commands, new behavior, new cooperative relationships

### Changed
- Modified behavior, updated defaults, restructured output

### Fixed
- Bug fixes, corrected documentation, removed stale content

### Removed
- Deleted commands, dropped dependencies, removed files

```

### Rules

- Use the `[X.Y.Z]` semver format for the header, not a date-only header
- Date format: `YYYY-MM-DD`
- Include only section headers that have entries — omit empty sections
- Each bullet is a single concise sentence. No nested bullets.
- Do not include implementation details or rationale in changelog bullets — state what changed, not why

---

## Versioning

All OCAS skills use semantic versioning (`MAJOR.MINOR.PATCH`).

| Change type | Version segment |
|---|---|
| Bug fix, text correction, stale content removal, cleanup | PATCH |
| New behavior, new command, new cooperative relationship, new output section | MINOR |
| Breaking change, architectural overhaul, new subsystem | MAJOR |

**Versioning applies consistently across:**
- The `version:` field in SKILL.md frontmatter
- The `## [X.Y.Z]` header in CHANGELOG.md
- The GitHub release tag (`vX.Y.Z`)
- The README.md Changelog section entry

All four must be in sync after every release.

---

## GitHub Releases

Every version bump requires a GitHub release.

| Field | Value |
|---|---|
| Tag | `vX.Y.Z` |
| Title | `vX.Y.Z` |
| Body | The CHANGELOG.md entry body for this version (without the `## [X.Y.Z] - date` header line) |
| Latest | Always mark as latest unless it is a hotfix for an older major version |

Release body format mirrors the CHANGELOG entry:
```
### Added
- ...

### Fixed
- ...
```

---

## Sync checklist

Before pushing a version bump:

- [ ] `version:` in SKILL.md frontmatter updated
- [ ] CHANGELOG.md entry prepended (most recent at top)
- [ ] README.md Changelog section updated with new entry
- [ ] All four version references match (`SKILL.md`, `CHANGELOG.md`, `README.md`, release tag)
- [ ] GitHub release created with tag `vX.Y.Z` and CHANGELOG body as release notes
- [ ] Behavioral config documented as `skills.config.<key>` in both SKILL.md and README (no env-var names); no `GENIE_*`/`<NAME>_*` reads remain in `scripts/`
