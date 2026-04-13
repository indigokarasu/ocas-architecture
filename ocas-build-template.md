# OCAS Skill Build Template

Version: 2.2.0
Author: Indigo Karasu

Changes from 2.1.0: updated storage requirements to central ~/openclaw/ layout; added journal path requirement; added interfaces section; added spec file reference table; clarified visibility and journal type requirements.

---

## Purpose

This document is the single implementation spec for a coder LLM. It must be fully self-contained. The coder generates a complete Agent Skill package from this file alone.

The output is the actual skill package -- not a planning memo, not a worksheet, not a commentary-heavy response.

---

## Skill Identity

### Skill name
`ocas-{skill}`

### Author metadata
- Author: Indigo Karasu
- Email: mx.indigo.karasu@gmail.com

### Skill type
Choose one: shortcut / workflow / system

### One-sentence build objective
State exactly what the skill must enable.

---

## Build Rules

The coder must:
- Build a real Agent Skill package
- Keep SKILL.md lean, operational, and routing-aware
- Include only files that materially improve behavior or reliability
- Prefer examples, schemas, and exact instructions over long explanation
- Define every required term locally
- Avoid process language about design phases, approvals, or prior documents
- Avoid mentioning absent resources, hidden context, or internal pipeline assumptions
- Optimize the package for actual use, not documentation completeness

---

## Required Output

Minimum structure unless the specification below requires more:

```
ocas-{skill}/
  SKILL.md
  README.md
  CHANGELOG.md
```

`skill.json` is the legacy format and should not be created for new packages. SKILL.md frontmatter (YAML) is the current standard.

`README.md` and `CHANGELOG.md` are required for every package. Follow the structure defined in `spec-ocas-skill-publishing.md`.

Add only justified support directories:

```
ocas-{skill}/
  references/
  scripts/
  assets/
```

---

## Package Specification

### skill.json

Minimum required fields:
- `name`: `ocas-{skill}`
- `version`: `{version}`
- `description`: routing-optimized text
- `author`: `Indigo Karasu`
- `email`: `mx.indigo.karasu@gmail.com`

### Description Requirements

The description must:
- State what the skill does
- State when it should be used
- Use natural request language where appropriate
- Optimize for routing and discoverability
- Avoid vague labels and branding-heavy language

### SKILL.md

The main operational file. Tells the agent:
- When to use the skill
- What the skill is responsible for
- How to execute the task
- When to consult any support file

Keep only load-bearing content in SKILL.md.

---

## SKILL.md Shape by Skill Type

### Shortcut (20–120 lines)
Sections: title, when to use, quick actions or commands, important inputs or options, failure cases or caveats.

### Workflow (80–250 lines)
Sections: title, when to use, inputs and assumptions, ordered workflow, output requirements, boundaries and pitfalls.

### System (150–300 lines)
Sections: title, trigger conditions, purpose and boundaries, decision model, execution loop, support file map, storage layout, validation rules.

---

## Storage Requirements

Every skill with persistent state uses these paths. No data inside the skill package.

```
~/openclaw/data/{skill-name}/config.json    — skill configuration
~/openclaw/data/{skill-name}/*.jsonl        — append-only logs
~/openclaw/journals/{skill-name}/YYYY-MM-DD/{run_id}.json  — journal files
```

For LadybugDB skills only:
```
~/openclaw/db/{skill-name}/{skill-name}.lbug
```

Config must include ConfigBase fields. See `spec-ocas-shared-schemas.md`.

### Storage Layout Section (required in system skill SKILL.md)

```
~/openclaw/data/ocas-{skill}/
  config.json
  {primary_log}.jsonl
  decisions.jsonl
~/openclaw/journals/ocas-{skill}/
  YYYY-MM-DD/{run_id}.json
```

---

## Journal Requirements

Every skill run writes a journal. Runs missing journals are invalid.

Declare which journal type(s) this skill emits:
- **Observation Journal** — signals discovered, no external side effects
- **Action Journal** — external side effects executed
- **Research Journal** — structured multi-source research sessions

Skills may emit multiple types depending on the command being run.

Journal path: `~/openclaw/journals/ocas-{skill}/YYYY-MM-DD/{run_id}.json`

See `spec-ocas-journal.md` for the full journal specification.

---

## Inter-Skill Interfaces

If this skill sends signals to or receives signals from another skill, specify the intake path and format here. Reference `spec-ocas-interfaces.md` for all defined interfaces.

Do not create undocumented inter-skill interfaces.

---

## Support File Rules

### references/
Create only when material is too detailed for SKILL.md. For each file: filename, purpose, exactly when SKILL.md should direct the agent to read it.

### scripts/
Create only when deterministic help materially improves correctness. For each script: filename, language/runtime, exact purpose, inputs, outputs.

### assets/
Create only when the skill ships useful reusable artifacts. For each asset: filename, purpose, how the agent should use it.

---

## Required Structural Sections

Every system skill SKILL.md must include:

**Responsibility Boundary** — what this skill does, what it does not do, which other skill owns the adjacent responsibility.

**Optional Skill Cooperation** — skills this skill may cooperate with when present, but never depend on.

**Journal Outputs** — which journal type(s) this skill emits and under what conditions.

**Storage Layout** — data and journal paths under `~/openclaw/`.

**Visibility** — `public` or `private`.

---

## Specificity Map

Be exact about: naming, file paths (use `~/openclaw/` root), metadata fields, command syntax, schemas, validation checks, routing language, journal types.

Allow flexibility in: prose descriptions, section ordering within guidelines, minor wording variation.

---

## Validation Requirements

### Routing Validation
Provide realistic prompts that should trigger the skill.
Provide realistic prompts that should not trigger the skill.
The description and SKILL.md must support that separation.

### Structural Validation
Confirm:
- All required files exist
- Filenames are consistent
- Support directories exist only when justified
- SKILL.md points to any support file it depends on
- Storage paths use `~/openclaw/` root
- Journal path is declared
- Major duplication across files has been avoided

### Usefulness Validation
Confirm:
- The skill has one sharp promise
- First useful action is obvious
- Instructions are specific where failure is costly
- The package is concise enough to be maintainable

---

## Reference Specifications

All OCAS skills are built against these specifications:

| File | Purpose |
|---|---|
| `spec-ocas-architecture.md` | System layers, data flow, skill registry |
| `spec-ocas-storage-conventions.md` | Storage roots, file types, retention |
| `spec-ocas-journal.md` | Journal structure, OKRs, champion/challenger |
| `spec-ocas-ontology.md` | Entity types, relationships, identity model |
| `spec-ocas-shared-schemas.md` | Canonical cross-skill data objects |
| `spec-ocas-interfaces.md` | Inter-skill communication paths and formats |
| `ocas-skill-authoring-rules.md` | Design principles, validation standard |

---

## Final Response Format for the Coder

Return:
1. Package tree
2. Full contents of every file
3. A brief validation summary

Do not return planning commentary, process narration, or references to external documents unless the build spec explicitly requires it.

---

## Fill-In Block

Complete this block before giving the document to the coder LLM.

### Skill Summary
- Skill name:
- Version:
- Skill type:
- One-sentence build objective:
- Visibility:

### Routing Description Draft
- Description:

### Required Files
- `skill.json`:
- `SKILL.md`:
- Additional files:

### SKILL.md Required Sections
- Section list:

### Support Files
- `references/`:
- `scripts/`:
- `assets/`:

### Storage Layout
- Data path: `~/openclaw/data/ocas-{skill}/`
- Journal path: `~/openclaw/journals/ocas-{skill}/`
- DB path (if applicable): `~/openclaw/db/ocas-{skill}/`

### Journal Output
- Journal type(s):
- Conditions for each type:

### Inter-Skill Interfaces
- Sends to:
- Receives from:

### Exact Constraints
- Naming:
- Paths:
- Metadata:
- Commands/schemas:
- Validation checks:

### Required Structural Sections
- Responsibility Boundary:
- Optional Skill Cooperation:
- Journal Outputs:
- Visibility:

### Trigger Tests
- Should trigger:
- Should not trigger:
