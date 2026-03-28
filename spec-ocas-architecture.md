# OCAS Architecture Overview

Spec Version: 1.3
Author: Indigo Karasu

Changes from 1.2: updated improvement loop to include Fellow as empirical evaluation engine between Mentor and Forge; updated Mentor description to include Workflow Plans system; updated shared schemas list to include ExperimentRequest, CycleResult, InsightProposal, BehavioralSignal, VariantProposal, VariantDecision; updated interfaces section to reference new Mentor↔Fellow intake paths; added spec-ocas-workflow-plans.md to specification index.

Changes from 1.2: noted Relay as not yet active, with build spec in Todo/Relay/.

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

### Preference Layer

Skills that maintain user preference models.

- **Taste** — behavior-driven taste model. Builds recommendations from consumption signals with evidence-backed explanations.

### System Evolution Layer

Skills that improve the system itself.

- **Mentor** — orchestration and evaluation engine. Manages long-running workflows (including named Workflow Plans), analyzes journals from all skills, evaluates champion vs. challenger variants, and proposes skill improvements to Forge. Routes experiments to Fellow for empirical evaluation. Reads journals directly for evaluation (parallel to Elephas ingestion).
- **Fellow** — empirical experimentation engine. Invoked exclusively by Mentor via intake file drop. Establishes a fresh baseline, generates and tests controlled variants within a constrained mutation surface, and returns the winning result with full lineage via CycleResult to Mentor's intake. Stores experiment lineage through Elephas.
- **Forge** — skill architect and builder. Designs, builds, and validates Agent Skill packages. Consumes variant proposals from Mentor. Emits complete installable packages.

### Interface Surfaces

- **Vesper** — daily briefing generator. Aggregates signals from Corvus, Dispatch, Rally, and other skills into morning and evening briefings. Presents outcomes without exposing internal processes.
- **Relay** — device gateway. Normalizes inbound device signals and manages permissions. Private skill. Build spec exists in `Todo/Relay/`; not yet active.

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

All persistent data is stored centrally under `~/openclaw/`, not inside skill packages or workspace dot-folders.

See `spec-ocas-storage-conventions.md` for the full standard.

```
~/openclaw/
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
| Taste | Observation |
| Rally | Observation, Action |
| Thread | Observation |
| Weave | Observation, Action (sync/writeback) |
| Elephas | Action |
| Praxis | Action |
| Dispatch | Action |
| Voyage | Action |
| Vesper | Action |
| Forge | Action |
| Mentor | Action |
| Fellow | Action |

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

- **Private skills** (must not be published or distributed): Dispatch, Relay, Thread
- **All others**: public

---

## Invariants

- Only Elephas writes to Chronicle.
- Only Weave writes to `~/openclaw/db/ocas-weave/`.
- Only Elephas writes to `~/openclaw/db/ocas-elephas/`.
- No skill reads or writes another skill's data directory.
- Challenger variants never execute side effects.
- Journals are append-only and immutable after write.
- Skills must function independently even when cooperating skills are absent.
- Private skills must never be published or distributed.
- All inter-skill data sharing uses defined intake paths or Chronicle/Weave queries.
