# spec-ocas-skill-improvements.md

Spec Version: 1.0.0
Author: Indigo Karasu

---

## Purpose

This specification defines a comprehensive set of architectural and authoring enhancements for OCAS Agent Skills. These improvements synthesize industry best practices from:
- **Hermes Agent** (Nous Research): Conditional activation, fallback skills, skill bundles, progressive disclosure knowledge-base skills, and write approval gating.
- **AgentSkills.io** (Open Standard): Standardized directory structures and progressive disclosure discovery.
- **Skillgrade** (mgechev / Open Ecosystem): Declarative evaluation suites (`eval.yaml`), multi-trial benchmarking, pass-rate thresholds, and automated regression detection.
- **Anthropic Engineering** ("Writing tools for agents"): Ergonomic tool design, context-aware verbosity formats (`concise` vs `detailed`), actionable error envelopes, task-grounded evaluations, and namespacing.

All improvements described in this document are designed to seamlessly integrate with and strictly preserve core **OCAS Architectural Invariants**.

---

## Summary of Preserved OCAS Invariants

Every enhancement in this specification respects the non-negotiable OCAS system invariants:

1. **Centralized Storage**: All skill state, configurations, benchmark logs, and staged patches reside centrally under `{agent_root}/commons/` (under `data/`, `journals/`, or `db/`), never inside skill package directories or workspace dot-folders.
2. **Mandatory Immutable Journaling**: Every operational run or evaluation task emits an append-only, immutable journal entry (Observation, Action, or Research) recorded in `{agent_root}/commons/journals/`.
3. **Empirical Improvement Loop**: Mentor (`ocas-mentor`) evaluates skill performance and proposes variants; Fellow (`ocas-fellow`) executes empirical benchmarks; Forge (`ocas-forge`) constructs skill packages.
4. **Exclusive Database Boundaries**: Only `ocas-elephas` writes to Chronicle (`commons/db/ocas-elephas/`); only `ocas-weave` writes to Weave (`commons/db/ocas-weave/`).
5. **Decoupled Inter-Skill Interfaces**: Skills communicate exclusively via intake filesystem directories (`commons/data/{skill}/intake/`) or read-only queries.
6. **Recovery & Evidence Logging**: Scheduled tasks and automated evaluations log execution evidence and support gap detection and self-repair.

---

## 1. Evaluation & Benchmarking Infrastructure

### 1.1 Declarative Skill Benchmark Suites (`eval.yaml`)
To measure and prevent behavioral regression during skill iteration, skills may include a declarative evaluation suite in `references/evals/eval.yaml` (or drop-loaded into `ocas-fellow`).

#### Schema Structure
```yaml
version: "1"
defaults:
  agent: claude           # target runner (claude | gemini | codex | acp)
  trials: 5               # number of evaluation trials
  timeout: 300            # timeout per trial in seconds
  threshold: 0.85         # required pass rate for variant promotion
  grader_model: claude-3-5-haiku

tasks:
  - name: verify-lookup-accuracy
    instruction: |
      Use the sift tool to verify the founding date of Acme Corp and output JSON to answer.json.
    workspace:
      - src: fixtures/sample_query.json
        dest: query.json
    graders:
      - type: deterministic
        run: python3 graders/check_answer.py
        weight: 0.7
      - type: llm_rubric
        rubric: |
          Did the agent perform targeted queries without superfluous broad web scans?
        weight: 0.3
```

### 1.2 Execution in the Mentor ↔ Fellow Loop
1. **Trigger**: When `ocas-mentor` detects an OKR regression or pattern anomaly, it generates a `VariantProposal` and issues an `ExperimentRequest` drop to `ocas-fellow`'s intake.
2. **Isolation**: `ocas-fellow` executes the challenger variant (`ocas-{skill}-variant-{YYYYMMDD}`) inside an isolated Docker simulation container via `ocas-inception`. Challenger variants run with **zero external side effects**.
3. **Evaluation**: `ocas-fellow` executes the tasks in `eval.yaml` across $N$ trials.
4. **Result Reporting**: `ocas-fellow` compiles a `CycleResult` JSON file into `ocas-mentor`'s intake, recording pass rate, average runtime, token consumption, and grader breakdowns.

### 1.3 Pass-Rate Thresholds for Promotion
A challenger variant will only be promoted to champion status by `ocas-mentor` if:
- **Smoke Check**: Pass rate $\ge 0.85$ over 5 trials.
- **Reliability Check**: Pass rate $\ge 0.85$ over 15 trials for core execution skills.
- **No Regression**: Challenger pass rate strictly exceeds champion pass rate on the same benchmark suite.

---

## 2. Tool Ergonomics, Response Formatting & Error Envelopes

### 2.1 Context-Aware Response Format Enums (`concise` vs `detailed`)
High-volume tools and helper scripts (`scripts/*.py`) must optimize token consumption by offering context-aware verbosity formats.

- **`concise` (Default)**: Returns high-signal, human-interpretable fields (e.g., names, titles, key summary attributes). Reduces prompt context usage by 60–80%.
- **`detailed`**: Includes low-level technical identifiers (UUIDs, raw timestamps, internal keys, pagination tokens) required for downstream programmatic tool chaining.

#### Script Invocation Standard
```bash
python3 scripts/search.py query '{"term": "quantum computing", "format": "concise"}'
```

### 2.2 Actionable Error Envelopes
When a script or tool encounters invalid parameters, missing credentials, or API boundaries, it must return a structured JSON envelope containing actionable recovery guidance rather than raw tracebacks.

#### Error Envelope Schema
```json
{
  "error": "INVALID_PARAMETER_RANGE",
  "message": "The requested date range exceeds the 30-day query limit.",
  "actionable_guidance": "Reduce 'date_range_days' parameter to <= 30 or invoke 'search.py' with page-based pagination.",
  "details": {
    "provided_days": 45,
    "max_allowed": 30
  }
}
```

### 2.3 Single-Intent Consolidated Action Wrappers
In alignment with Anthropic's tool design principles and Core Rules #1 & #2:
- Avoid multi-step primitive tool chains (e.g., forcing the agent to execute `list_users` $\rightarrow$ `check_availability` $\rightarrow$ `book_slot`).
- Provide consolidated action wrappers in `scripts/` (e.g., `schedule_meeting.py`) that handle intermediate lookups internally and return a single, high-signal result.

---

## 3. Skill Metadata, Conditional Activation & Skill Bundles

### 3.1 Conditional Activation & Fallback Declarations
Skills may specify conditional activation criteria in `skill.json` under `metadata.activation` to prevent trigger clutter and manage tool dependencies.

#### `skill.json` Activation Extension
```json
{
  "name": "ocas-google-workspace",
  "version": "1.2.0",
  "metadata": {
    "activation": {
      "requires_tools": ["workspace_mcp"],
      "fallback_for_tools": ["google_api_fallback"],
      "requires_environment": ["GOOGLE_WORKSPACE_CREDENTIALS"]
    }
  }
}
```

- `requires_tools`: Skill is loaded into context only when listed toolsets are present.
- `fallback_for_tools`: Skill is activated as a fallback when primary tools are absent.

### 3.2 Bundled Skill Aliases (`references/bundles/`)
Skills that regularly operate together in complex multi-skill workflows ship bundled plan aliases in `references/bundles/{bundle_id}.yaml`.

#### Bundle Schema Example (`references/bundles/contact-investigation.yaml`)
```yaml
name: contact-investigation
description: Complete contact research and relationship context pipeline.
skills:
  - ocas-scout
  - ocas-weave
  - ocas-sift
instruction: |
  Start by checking existing social context in Weave, then run Scout OSINT background check, and enrich missing company facts via Sift.
```

Bundling allows single-command invocation (`/contact-investigation "Jane Doe"`) while preserving individual skill boundaries.

---

## 4. Knowledge-Base Skill Synthesis & Progressive Disclosure

### 4.1 Modular Reference Splitting
When an OCAS skill encompasses extensive domain knowledge (e.g., legal specs, research guidelines, complex API docs), the skill follows a 3-level progressive disclosure structure:

- **Level 0 (Discovery)**: `skill.json` description ($\le 60$ chars).
- **Level 1 (Activation)**: `SKILL.md` (150–300 lines) containing core decision logic, trigger criteria, and a reference file map.
- **Level 2 (Deep Context)**: Topic-specific reference files in `references/{topic}.md`.

#### Rules for Knowledge-Base Skills
1. `SKILL.md` must explicitly list every reference file and specify *when* and *why* the agent should inspect it.
2. `references/` directory must not exceed 60 reference files to prevent context sprawl.
3. Reference files cost zero context tokens until loaded explicitly by the agent.

---

## 5. Quality Auditing, Linting & Staged Write Approval

### 5.1 Automated Skill Quality Linters (`ocas-forge`)
`ocas-forge` and pre-commit checks enforce the following static quality constraints:

- **Frontmatter Verification**: Validates required metadata fields (`name`, `description`, `version`, `author`).
- **Incident Log Shape Detection**: Flags skill descriptions or reference bodies that are overly dense in ephemeral issue numbers or quoted chat transcripts instead of generalizable rules.
- **Reference Sprawl Check**: Fails build if `references/` contains $> 60$ files.
- **Config vs Env Separation**: Rejects scripts that read behavioral configuration from `os.environ` instead of `skills.config.<key>` in `config.yaml`.

### 5.2 Staged Write Approval Gate
Automated skill edits generated by system evolution skills (`ocas-praxis`, `ocas-finch`) must be staged prior to deployment:

1. Proposed modifications are written to `{agent_root}/commons/data/ocas-forge/staged/{skill_name}/`.
2. `ocas-mentor` schedules an empirical benchmark run with `ocas-fellow`.
3. Upon successful pass-rate verification, `ocas-mentor` emits a `VariantDecision` to `ocas-forge` to apply the staged patch to production.

---

## Specification Index Update

This specification is indexed in the OCAS Architecture Suite alongside:
- `spec-ocas-architecture.md`
- `ocas-skill-authoring-rules.md`
- `spec-ocas-scripts.md`
- `spec-ocas-shared-schemas.md`
- `spec-ocas-workflow-plans.md`
