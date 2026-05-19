# OCAS Architecture Overview

Spec Version: 1.4.1
Author: Indigo Karasu

Changes from 1.4: updated Lucid description from "purpose under review" to its documented role (nightly journal curator, MemPalace ingestion via MCP, introduced in lucid v2.0.2).

Changes from 1.3: coherence audit 2026-05-19 discovered 23 active OCAS skill repositories; added ocas-reach (Signal Layer), ocas-imagine (Execution Layer), ocas-google-workspace (Execution Layer), ocas-finch (System Evolution Layer), and ocas-lucid (Execution Layer) to the skill registry; re-activated 17 previously-archived skills (scout, sift, look, corvus, elephas, weave, praxis, voyage, rally, sands, custodian, taste, mentor, fellow, forge, vesper, bower, spot) whose GitHub repositories now exist; updated journal types table and cooperation flow to cover newly active skills; Relay removed from Interface Surfaces (repo still absent).

Changes from 1.2: updated improvement loop to include Fellow as empirical evaluation engine between Mentor and Forge; updated Mentor description to include Workflow Plans system; updated shared schemas list to include ExperimentRequest, CycleResult, InsightProposal, BehavioralSignal, VariantProposal, VariantDecision; updated interfaces section to reference new Mentor↔Fellow intake paths; added spec-ocas-workflow-plans.md to specification index.

---

## Purpose

This document describes the overall architecture of the OCAS ecosystem. It defines the system layers, data flow between skills, and the role of each skill within the architecture.

Any skill author, coder LLM, or orchestration system should consult this document to understand where a skill fits and how it interacts with other components.

---

## System Layers

### Signal Layer

Skills that observe, discover, and extract structured information from the environment.

- **Corvus** — exploratory pattern analysis across the knowledge graph and skill journals. Detects routines, threads, interests, anomalies, and opportunities. Emits InsightProposals to Vesper and behavioral signals to Praxis.
- **Scout** — investigative OSINT research on people and organizations. Produces provenance-backed briefs.
- **Sift** — web search, topic research, fact verification, and entity extraction. The system's general research engine.
- **Look** — image-to-action processing. Converts user-provided images into validated, decision-ready drafts.
- **Reach** — live world-data query engine. Normalizes queries across external data sources and returns structured results to calling skills.
- **Thread** — personal web activity interpretation. Reconstructs browsing sessions and research threads from browser signals. Private skill.

### Memory Layer

Skills that maintain durable structured knowledge.

- **Elephas (Chronicle)** — the system's long-term knowledge graph. Ingests journals from all skills, promotes facts, resolves entity identity, and generates behavioral inferences. Only Elephas writes to Chronicle.
- **Weave** — the social relationship graph. Maintains provenance-backed records of people, relationships, preferences, and shared experiences. Standalone LadybugDB database.

### Execution Layer

Skills that plan and execute actions in the world.

- **Praxis** — behavioral refinement loop. Captures outcomes, extracts lessons, and maintains bounded active behavior shifts. Receives behavioral signals from Corvus. Proposes skill rebuilds to Forge.
- **Voyage** — travel planning, itinerary construction, and reservation management.
- **Dispatch** — communications management. Inbox triage, thread tracking, draft generation, and identity-safe public communication. Private skill.
- **Rally** — governed portfolio research, candidate scoring, allocation planning, and trade planning.
- **Sands** — calendar management. Natural-language scheduling, conflict detection, travel time insertion via Google Places API, and schedule brief emission to Vesper.
- **Custodian** — system health monitoring. Error diagnosis, data integrity checks, and self-healing automation.
- **Imagine** — art-direction engine for text-to-image generation. Applies the Narrative Style Creation & Transfer methodology to produce professionally art-directed image prompts and generation workflows.
- **Google-Workspace** — Google Workspace integration. Provides Google Drive, Docs, Sheets, Calendar, and Gmail access via Workspace MCP with a `google_api.py` script fallback.
- **Lucid** — nightly journal curator. Batch-processes OCAS skill journals into MemPalace's verbatim store via MCP tools. Runs as a scheduled cron job at 3am, classifying each journal for filing as a MemPalace drawer entry.

### Preference Layer

Skills that maintain user preference models.

- **Taste** — behavior-driven taste model. Builds recommendations from consumption signals with evidence-backed explanations.

### System Evolution Layer

Skills that improve the system itself.

- **Mentor** — orchestration and evaluation engine. Manages long-running workflows (including named Workflow Plans), analyzes journals from all skills, evaluates champion vs. challenger variants, and proposes skill improvements to Forge. Routes experiments to Fellow for empirical evaluation. Reads journals directly for evaluation (parallel to Elephas ingestion).
- **Fellow** — empirical experimentation engine. Invoked exclusively by Mentor via intake file drop. Establishes a fresh baseline, generates and tests controlled variants within a constrained mutation surface, and returns the winning result with full lineage via CycleResult to Mentor's intake. Stores experiment lineage through Elephas.
- **Forge** — skill architect and builder. Designs, builds, and validates Agent Skill packages. Consumes variant proposals from Mentor. Emits complete installable packages.
- **Finch** — session self-improvement orchestrator. Mines agent session JSONL files to detect corrections, breakthroughs, methodologies, and behavioral directives. Routes findings to MEMORY.md and skill patches. Named for Darwin's finch; adaptive evolution of the system.

### Interface Surfaces

- **Vesper** — daily briefing generator. Aggregates signals from Corvus, Dispatch, Rally, Sands, and other skills into morning and evening briefings. Presents outcomes without exposing internal processes.
- **Haiku** — social media presence management for Bluesky. Content strategy, post generation with human-writing quality gate, follow maintenance, and haiku practice. No active repository as of 2026-05-19.

---

## Data Flow

### Journal Flow

Every skill run writes a journal. Elephas and Mentor are parallel consumers with different purposes.

```
All Skills → journals/
             ├── Elephas (ingestion → Chronicle facts)
             └── Mentor (evaluation → OKR scoring, variant proposals → Forge)
```

Elephas ingests journal entity signals into Chronicle (knowledge graph).
Mentor reads journals for performance evaluation and skill improvement.
These are independent reads. Neither blocks the other.

### Improvement Loop

```
Mentor (detects OKR regression or pattern)
  → VariantProposal → Forge (builds variant skill package)
  → ExperimentRequest → Fellow (empirical benchmark evaluation)
  → CycleResult → Mentor (promote | no_change | abort decision)
  → VariantDecision → Forge (applies promotion if approved)
```

Mentor writes ExperimentRequest files to Fellow's intake. Fellow runs controlled experiments and writes CycleResult to Mentor's intake. Mentor then emits a VariantDecision to Forge. All handoffs are filesystem drops to intake directories.

Corvus contributes to the improvement loop by detecting behavioral anomalies in skill output patterns and emitting signals that Praxis records as events:

```
Corvus (detects behavioral anomaly in journals)
  → Signal → Praxis intake
  → Praxis (records event, may extract lesson, propose behavior shift)
```

### Query Flow

```
Any Skill → Elephas.query (world knowledge from Chronicle)
Any Skill → Weave.query (social graph, read-only)
```

Chronicle is read-only for all skills except Elephas. Weave is read-only for all skills except Weave itself.

### Cooperation Flow

Skills may cooperate when present but must never depend on each other.

```
Sift → Weave (entity disambiguation)
Sift → Thread (recent browsing context for query rewriting)
Scout → Weave (identity context)
Taste → Sift (item enrichment)
Corvus → Elephas (graph context for pattern analysis)
Look → Sift (web research for validation)
Vesper → Corvus (receives opportunity signals)
Dispatch → Praxis (receives action decisions)
Rally → Vesper (portfolio outcome signals)
Thread → Corvus (research thread signals)
Thread → Elephas (Chronicle candidates)
```

### Briefing Flow

```
Corvus → opportunity signals
Dispatch → communication summaries    ┐
Rally → portfolio outcomes            ├→ Vesper → briefing → Dispatch (delivery)
Calendar / Weather / Context          ┘
```

---

## Naming Convention

All skills use hyphenated identifiers: `ocas-scout`, `ocas-rally`, `ocas-taste`.

Dots must not be used because some runtimes interpret them as hierarchy separators.

---

## Storage Convention

All persistent data is stored centrally under `{agent_root}/commons/`, not inside skill packages or workspace dot-folders.

See `spec-ocas-storage-conventions.md` for the full standard.

```
{agent_root}/commons/
  data/{skill-name}/     — skill state, config, JSONL logs
  journals/{skill-name}/ — journal files
  db/{skill-name}/       — LadybugDB databases (Elephas, Weave only)
```

---

## Inter-Skill Communication

Skills communicate through shared filesystem paths, not direct calls.

See `spec-ocas-interfaces.md` for all intake directories, signal formats, and handoff contracts.

---

## Journal Types

See `spec-ocas-journal.md` for the full journal specification.

Three formal types:

- **Observation Journal** — signals discovered by the system
- **Action Journal** — actions executed by the system
- **Research Journal** — research sessions and sources

Journal type by skill:

| Skill | Journal Type |
|---|---|
| Corvus | Observation |
| Scout | Observation, Research |
| Sift | Observation, Research |
| Look | Observation |
| Reach | Observation, Research |
| Taste | Observation |
| Rally | Observation, Action |
| Thread | Observation |
| Weave | Observation, Action (sync/writeback) |
| Bower | Observation, Action |
| Elephas | Action |
| Praxis | Action |
| Dispatch | Action |
| Voyage | Action |
| Sands | Action |
| Custodian | Action |
| Imagine | Action |
| Google-Workspace | Action |
| Lucid | Action |
| Vesper | Action |
| Forge | Action |
| Mentor | Action |
| Fellow | Action |
| Finch | Action |
| Spot | Action |

---

## Ontology

See `spec-ocas-ontology.md` for the shared entity type hierarchy and identity model.

Chronicle (Elephas) is the authoritative store. All skills that extract or reference entities use the shared ontology.

---

## Shared Schemas

See `spec-ocas-shared-schemas.md` for canonical cross-cutting data objects: DecisionRecord, Signal, Candidate, JournalEntry, ConfigBase, LogEvent, SkillStatus, InsightProposal, BehavioralSignal, VariantProposal, VariantDecision, ExperimentRequest, CycleResult.

---

## Interfaces

See `spec-ocas-interfaces.md` for:
- all inter-skill intake directory contracts
- signal delivery formats
- the Corvus→Praxis behavioral signal path
- the Mentor→Forge variant proposal and decision paths
- the Mentor→Fellow ExperimentRequest path
- the Fellow→Mentor CycleResult path
- the Elephas signal intake path
- the Thread→Corvus and Thread→Elephas paths

See `spec-ocas-workflow-plans.md` for:
- the Workflow Plans format and parameter system
- plan run tracking and state schema
- invocation patterns (manual, cron, heartbeat)

---

## Visibility

- **Private skills** (must not be published or distributed): Dispatch, Thread
- **All others**: public
- **No active repository as of 2026-05-19**: Haiku, Dispatch, Thread, Relay

---

## Invariants

- Only Elephas writes to Chronicle.
- Only Weave writes to `{agent_root}/commons/db/ocas-weave/`.
- Only Elephas writes to `{agent_root}/commons/db/ocas-elephas/`.
- No skill reads or writes another skill's data directory.
- Challenger variants never execute side effects.
- Journals are append-only and immutable after write.
- Skills must function independently even when cooperating skills are absent.
- Private skills must never be published or distributed.
- All inter-skill data sharing uses defined intake paths or Chronicle/Weave queries.
