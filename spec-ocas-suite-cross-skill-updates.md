# spec-ocas-suite-cross-skill-updates.md

Spec Version: 1.0.0
Author: Indigo Karasu

---

## Purpose

This specification defines the comprehensive cross-skill update plan for all active components in the OCAS Agent Suite (`indigokarasu`). It synthesizes cross-pollinated learnings from across the suite alongside the standards introduced in `spec-ocas-skill-improvements.md` (evaluations, response formatting, error envelopes, conditional activation, and config policies).

---

## Inventory & Visibility Reconciliation

The live inventory of active components in the OCAS suite comprises:

- **Public Repositories**: `bower`, `chronicle-agent-context-and-memory`, `custodian`, `fellow`, `finch`, `forge`, `genie`, `get-md`, `imagine`, `look`, `lucid`, `mentor`, `multipass`, `praxis`, `reach`, `sands`, `scout`, `sift`, `skilllab`, `spot`, `styx`, `taste`, `vesper`, `voyage`, `weave`.
- **Private Repositories**: `dispatch`, `thread`, `bones` (formerly `odds`), `inception`, `haiku`, `rally`.
- **Archived / Superseded**: `ocas-elephas` (superseded by `chronicle-agent-context-and-memory` plugin), `corvus` (superseded by `finch` and `mentor`), `relay`, `triage`, `vibes`.

---

## Suite-Wide Cross-Skill Upgrades by Layer

### 1. Memory Layer

#### Chronicle Plugin (`chronicle-agent-context-and-memory`)
- **Stale Lock Recovery**: Implement automated stale SQLite file lock cleanup (`.db-wal` / `.db-shm`) per `spec-ocas-recovery.md`.
- **Skill-Namespaced Pointer Ingestion**: Store reference pointers (`weave:person_id`, `scout:subject_id`, `rally:ticker`) rather than duplicating raw skill payloads into Chronicle.

#### `ocas-weave` (`indigokarasu/weave`)
- **Concise Read Formatting**: Support read-only `--format=concise` output mode for `sift` and `scout` during identity disambiguation queries.

---

### 2. Signal Layer

#### `ocas-sift` (`indigokarasu/sift`)
- **Local SearXNG Cascade**: Embed local SearXNG fallback (port 8888) when primary web search APIs hit rate limits.
- **Context-Aware Output**: Implement `--format=concise` (clean title/url/snippet JSON saving ~70% context tokens) and `--format=detailed` opt-in.
- **Extraction Tooling**: Standardize `get-md` (`indigokarasu/get-md`) as the default HTML-to-Markdown extraction engine.
- **Eval Suite**: Add `references/evals/eval.yaml` testing fact extraction precision.

#### `ocas-scout` (`indigokarasu/scout`)
- **Dossier Storage**: Store intermediate OSINT research at `{agent_root}/commons/data/ocas-scout/dossiers/{SUBJECT}.md`.
- **MCP Discovery Cache**: Standardize 24-hour TTL caching on MCP server discovery probes via `MCPDiscoveryRecord`.

#### `ocas-look` (`indigokarasu/look`)
- **Structured Action Envelopes**: Format visual extraction output into structured action drafts with explicit `confidence` and `requires_confirmation` fields.

#### `ocas-reach` (`indigokarasu/reach`)
- **Actionable Error Envelopes**: Wrap external API errors in JSON envelopes containing actionable retry backoff guidance per `spec-ocas-scripts.md`.

---

### 3. Execution Layer

#### `ocas-rally` (Private — `indigokarasu/rally`)
- **Research Dossiers**: Maintain research dossiers at `{agent_root}/commons/data/ocas-rally/research_dossiers/{TICKER}.md`.
- **Local SearXNG Sentiment**: Direct SearXNG fallback (`rally_data_sources.py`) on port 8888 for `social_heat` queries when `sift` is absent.
- **Eval Suite**: Add `references/evals/eval.yaml` testing factor scoring stability and delta-based signal emission across historical market snapshots.

#### `ocas-praxis` (`indigokarasu/praxis`)
- **Staged Behavior Shift Approval**: Route proposed behavior shifts and skill rebuilds to `{agent_root}/commons/data/ocas-forge/staged/` for benchmark verification before committing.

#### `ocas-voyage` (`indigokarasu/voyage`)
- **Intake Brief Delivery**: Deliver travel schedule briefs directly to `ocas-vesper`'s intake directory (`{agent_root}/commons/data/ocas-vesper/intake/`).
- **Bundled Plan**: Ship `references/plans/trip-planning.plan.md`.

#### `ocas-sands` (`indigokarasu/sands`)
- **Activation & Fallback Declarations**: Declare `metadata.activation.requires_tools: ["workspace_mcp"]` and `fallback_for_tools: ["google_api_fallback"]`.

#### `ocas-custodian` (`indigokarasu/custodian` & `hermes-custodian-plugin`)
- **Two-Stage Self-Healing**: Enforce decision logging before execution $\rightarrow$ attempt repair $\rightarrow$ execute mandatory re-validation check before logging success.
- **Log Compaction**: Compact recovery evidence logs when exceeding 1,000 entries per `spec-ocas-recovery.md`.

#### `ocas-imagine` (`indigokarasu/imagine`)
- **Concise Prompt Schemas**: Format art-direction output as structured JSON containing prompt text, style weights, and negative prompts.

#### `ocas-lucid` (`indigokarasu/lucid`)
- **Schedule Gap Recovery**: Implement morning gap detection to process missed 3am cron runs if system was asleep.

#### `ocas-bower` (`indigokarasu/bower`)
- **Workspace MCP Fallback**: Fall back gracefully to `google_api.py` when Workspace MCP is absent.

#### `ocas-spot` (`indigokarasu/spot`)
- **Brief Intake Emission**: Emit appointment confirmation briefs directly to `ocas-vesper` intake.

#### `ocas-genie` (`indigokarasu/genie`)
- **Config Migration**: Migrate all `GENIE_*` environment variable configuration settings to `config.yaml` (`skills.config.genie.*`) per standard.

---

### 4. Preference & Data Layer

#### `ocas-taste` (`indigokarasu/taste`)
- **Item Enrichment Query**: Invoke `sift` using `--format=concise` for item enrichment; fall back gracefully if `sift` is absent.
- **Bundled Plan**: Ship `references/plans/preference-scan.plan.md`.

#### `ocas-styx` (`indigokarasu/styx`)
- **Merchant Enrichment**: Enrich transaction records with `taste` categories and emit consumption signals to `taste` intake.

---

### 5. System Evolution Layer

#### `ocas-mentor` (`indigokarasu/mentor`)
- **Pass-Rate Promotion Thresholds**: Require $\ge 0.85$ pass rate across $N \ge 15$ trials from `ocas-fellow` before promoting challenger variants.

#### `ocas-fellow` (`indigokarasu/fellow`)
- **Skillgrade Evaluation Engine**: Native execution of `eval.yaml` suites in isolated `ocas-inception` containers. Returns `CycleResult` with trial pass rates, token metrics, and grader breakdowns.

#### `ocas-forge` (`indigokarasu/forge`)
- **Pre-Build Quality Linters**: Embed automated linting checks (max 60 reference files, incident-log shape, `config.yaml` policy).

#### `ocas-finch` (`indigokarasu/finch`)
- **Direct Lesson Extraction**: Mine session logs directly for corrections and stage proposed patches under `{agent_root}/commons/data/ocas-forge/staged/` for `ocas-fellow` evaluation.

#### `ocas-skilllab` (`indigokarasu/skilllab`)
- **Local Eval Runner**: Integrate `skillgrade` CLI tooling for local offline evaluation of `eval.yaml` suites prior to submitting variants.

---

### 6. Interface Surfaces

#### `ocas-vesper` (`indigokarasu/vesper`)
- **Intake Polling**: Poll intake for `sands`, `voyage`, and `spot` schedule briefs, and `taste` recommendation highlights.

#### `ocas-multipass` (`indigokarasu/multipass`)
- **Token Storage Discipline**: Standardize token storage under `~/.hermes/{service}_token.json` with token freshness validation prior to request execution.

---

## Specification Index Update

This specification is indexed in the OCAS Architecture Suite alongside:
- `spec-ocas-architecture.md`
- `ocas-skill-authoring-rules.md`
- `spec-ocas-skill-improvements.md`
- `spec-ocas-scripts.md`
