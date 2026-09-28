# OCAS Architecture Overview

Spec Version: 2.0.0  
Author: Indigo Karasu

## Purpose

OCAS is a suite of independently useful skills and Hermes runtime components coordinated through explicit contracts. This specification defines responsibility boundaries, durable-memory ownership, system layers, and architectural invariants. `components.json` is the canonical machine-readable component registry; this document is the human-readable system model.

## Core model

OCAS separates four concerns that older revisions conflated:

1. **Durable memory** — Chronicle, principal-scoped and provenance-backed.
2. **User understanding** — User Dreaming and user-context projections, owned by the user principal.
3. **Agent identity and growth** — the agent's autobiographical system, owned by the agent principal.
4. **Domain execution** — OCAS skills that observe, research, plan, act, evaluate, and communicate.

Chronicle is the durable memory/context substrate. It is not mediated by a special OCAS memory-writer skill. Components write or query Chronicle only through sanctioned Chronicle contracts and always as an explicit principal.

## Principal boundary

Every durable memory operation has an owner/principal.

- **user principal** — facts, episodes, preferences, interests, relationships, corrections, and derived understanding about the owner/user.
- **agent principal** — the agent's own autobiographical experiences, self-model, lessons, identity development, and agent-owned operational history.
- Additional principals may exist, but cross-principal access is explicit and ACL-governed.

Read permission never implies write ownership. A component may use evidence visible across a permitted boundary without transferring ownership of the derived record.

### Shared evidence, separate derivation

A conversation may simultaneously support:

- a user-owned memory, such as a preference or correction; and
- an agent-owned autobiographical lesson about how the interaction went.

Those are two records with separate principals, provenance, confidence, lifecycle, and retraction behavior. Evidence may be shared; derived identity may not be conflated.

## User Dreaming

**User Dreaming** is offline consolidation about the user only. It may connect temporally separated user evidence, resolve contradictions, identify repeated preferences/interests, and create derived user-memory candidates.

User Dreaming:

- reads user-owned Chronicle memory and eligible user-grounded evidence;
- distinguishes user-stated facts, observations, inference, prediction, and uncertainty;
- rejects circular reinforcement from its own previous summaries;
- records provenance for every accepted derivation;
- writes durable outputs only to the user principal;
- may feed rebuildable user-context projections;
- never changes the agent's identity/persona or activates agent behavioral shifts.

## Agent autobiographical growth

**Agent autobiographical growth** is a separate subsystem. It owns the agent's continuity, self-observation, dreams, mistakes, lessons, aesthetics, relationships, and evolving self-model.

It:

- writes only agent-owned autobiographical/identity state;
- may cite shared interaction evidence;
- does not manufacture user facts from agent reflection;
- does not rewrite user-owned Chronicle memories;
- remains authoritative for agent identity evolution.

User Dreaming and agent autobiographical growth may process the same source interaction independently. Neither is a stage of the other.

## Context and behavior projections

Durable memory is not the same as injected context or behavior.

- **Chronicle durable memory** — canonical principal-scoped memory/beliefs.
- **Agent autobiographical identity** — canonical agent self-history and self-model.
- **Behavioral shifts** — bounded agent behavior adjustments; owned by the agent side of the system.
- **Directive context** — compact always/never operational instructions injected into sessions; rebuildable and not a substitute for Chronicle.
- **User context projection** — compact current-state USER.md/Daily Context material; rebuildable from user signals/memory and not canonical durable memory.

## System layers

### Signal and research

Scout, Sift, Look, Reach, Thread, Bones and other domain observers collect or derive evidence. They retain domain-specific raw state locally and may propose durable memories through Chronicle contracts when evidence is worth preserving.

### Memory and relationship

- **Chronicle** — principal-scoped durable memory, beliefs, provenance, temporal context, retrieval and ACLs.
- **User Dreaming** — user-only offline synthesis and consolidation.
- **Lucid** — nightly journal curation for configured memory ingestion. Lucid is not the agent's autobiographical dream system and must not write unscoped/global memory.
- **Weave** — relationship/social-graph domain capability where deployed. Its private implementation state is not a general cross-skill datastore.
- **UserContext** — rebuildable current-state user projection.

### Execution

Praxis, Voyage, Dispatch, Rally, Sands, Custodian, Imagine and other domain skills plan or perform actions. External side effects follow recovery, approval and evidence contracts.

Praxis owns bounded agent behavioral adaptation. It does not own broad user autobiography or user durable memory.

### Preference

Taste owns domain preference modeling. Durable user preference claims promoted beyond Taste's local model are user-principal Chronicle records with provenance.

### System evolution

- **Mentor** — evaluation and improvement orchestration.
- **Fellow** — empirical experimentation.
- **Forge** — skill architecture, build and validation.
- **Finch** — session learning and compact directive-context maintenance.
- **Inception** — isolated environment simulation where deployed.
- **Agent autobiographical growth** — identity/self-development, separate from user memory and skill optimization.

### Interface surfaces

Vesper, Haiku and other presentation/delivery surfaces consume typed outputs without becoming owners of upstream durable state.

## Data flow

### Journals

Every skill run writes an immutable journal. Journals are telemetry/evidence, not automatically durable personal memory.

```text
All Skills -> journals/
              |-> Mentor/Fellow evaluation
              |-> Lucid curation
              `-> other explicitly documented consumers
```

A consumer may propose Chronicle records from a journal, but Chronicle promotion requires an explicit target principal, provenance and sanctioned write contract.

### User-memory consolidation

```text
user-grounded evidence
  -> Chronicle user principal
  -> User Dreaming
  -> verified derived user memories / temporal links / contradictions
  -> user-context projections as needed
```

Prior dream output is not independent evidence for itself.

### Agent growth

```text
agent behavior + interaction evidence
  -> agent autobiographical observations
  -> agent dream/reflection/growth pipeline
  -> canonical agent self-model
  -> bounded injected identity projection
```

This flow does not write user memory.

### Improvement loop

```text
Mentor -> VariantProposal -> Forge
Mentor -> ExperimentRequest -> Fellow
Fellow -> CycleResult -> Mentor
Mentor -> VariantDecision -> Forge
```

System improvement evidence may be stored as operational records but must not be confused with user or agent autobiographical memory.

## Inter-component communication

Use, in order of preference:

1. typed runtime/tool contract;
2. Chronicle query/write contract for durable memory;
3. documented intake queue under the consumer's interface path;
4. exported read-only projection explicitly documented for cooperative reads.

A component MUST NOT open another component's private data directory or database merely because the filesystem is reachable.

Filesystem intake delivery uses atomic write-then-rename, immutable messages, idempotency keys, schema versions, correlation/causation IDs, processed acknowledgement, retry policy and dead-letter handling. See `spec-ocas-interfaces.md`.

## Storage

Persistent OCAS state lives under `{agent_root}/commons/` according to `spec-ocas-storage-conventions.md`. Chronicle's own runtime storage is Chronicle-owned and is accessed through Chronicle contracts, not by opening database files from skills.

## Recovery

Scheduled and side-effecting components follow `spec-ocas-recovery.md`: durable intent before action, execution evidence on every run, idempotent retry, lease/reclaim semantics where concurrency exists, expected-outcome verification, degradation handling and repair re-validation.

## Registry and drift validation

`components.json` is the canonical component/status registry. Retired components are retained there only as migration/history metadata and MUST NOT reappear as active dependencies.

`python scripts/validate_architecture.py` validates core contracts. CI runs it on pushes and pull requests.

## Invariants

- Every durable memory write names an explicit target principal.
- User Dreaming writes only user-owned durable memory.
- Agent autobiographical growth writes only agent-owned identity/autobiographical state.
- Cross-principal reads require explicit authorization; read permission never grants write ownership.
- Agent-generated interpretations are not silently upgraded to user-authored evidence.
- Reprocessing the same evidence does not increase confidence merely through repetition.
- UserContext and directive files are projections, not canonical durable memory stores.
- No skill reads or writes another component's private data directory or private database.
- Journals are append-only and immutable after write.
- Challenger variants never execute external side effects.
- Skills degrade honestly when optional cooperating components are absent.
- Every scheduled run writes execution evidence, including deliberate no-ops.
- Self-repair is not successful until re-validation passes.
- Retired components cannot appear in active architecture contracts.

## Specification index

- components.json — canonical component registry and lifecycle state
- spec-ocas-component-registry.md — registry semantics and drift rules
- spec-ocas-principals-and-memory-boundaries.md — user/agent ownership, correction and erasure
- spec-ocas-user-dreaming.md — user-only offline consolidation
- spec-ocas-runtime-contracts.md — capabilities, credentials, task/provenance/artifact/introspection contracts
- spec-ocas-interfaces.md — cross-component communication
- spec-ocas-storage-conventions.md — private state, journals, queues, exports and runtime storage
- spec-ocas-shared-schemas.md — canonical cross-component objects
- spec-ocas-journal.md — immutable run/evaluation evidence
- spec-ocas-recovery.md — durable intent, leases, evidence and verified repair
- spec-ocas-workflow-plans.md — durable workflow plans
- spec-ocas-ontology.md — entity/relationship semantics
- spec-ocas-skill-improvements.md — evaluation and evolution
- ocas-skill-authoring-rules.md — authoring rules
- ocas-build-template.md — implementation template
