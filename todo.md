# OCAS Architecture TODO

Status: proposed  
Basis: live-repository audit plus reusable patterns identified in the Muse built-in skills/runtime review  
Scope: architecture-level changes only; provider-specific implementation work should be tracked in the owning repository.

> Privacy note: this public TODO describes private components by architectural role rather than exposing private repository names, implementation details, or data.

## Why this exists

The checked-in OCAS architecture has drifted materially from the running system. Several specifications and active skills still describe retired components and an obsolete memory stack. At the same time, newer runtime capabilities have created cleaner boundaries that the architecture has not yet documented.

This TODO has two goals:

1. Make the architecture describe the system that actually exists today.
2. Adopt the strongest reusable patterns from the Muse runtime without collapsing distinct OCAS responsibilities or creating duplicate systems.

The most important correction is conceptual:

- Chronicle is the durable memory/context substrate.
- User memory and agent memory are separate Chronicle principals/owners with explicit access boundaries.
- User-focused Dreaming is about the owner/user and writes only into the user memory domain.
- The agent's autobiographical growth/evolution system is separate and must remain separate.
- A shared interaction may be evidence for both systems, but derived claims, lifecycle, retraction, and runtime influence must remain subject-scoped.

---

# P0 — Restore architectural truth

## [ ] Replace the static component registry with a live, status-bearing registry

Create a canonical machine-readable registry, for example:

- component id
- repository
- visibility class
- component type: skill | plugin | runtime | support | data
- status: active | experimental | support | replaced | retired
- replacement component, when applicable
- owner layer
- interfaces provided/consumed
- install/restore inclusion
- public-description-safe flag

Generate the human-readable architecture index from this registry.

Acceptance criteria:

- Every live component has an explicit status.
- Replaced/retired components remain in history but cannot appear as active dependencies.
- CI fails when an active architecture reference names an unknown or retired component.
- Private component details are never emitted into public generated docs unless explicitly marked public-description-safe.

## [ ] Remove retired Elephas and Corvus assumptions everywhere

Elephas and Corvus are no longer active components, but stale references remain in architecture specs and several live skill contracts.

Known stale surfaces from the audit include:

- spec-ocas-architecture.md
- spec-ocas-interfaces.md
- spec-ocas-shared-schemas.md
- Lucid
- Sift
- Thread
- Haiku
- Bower
- restore/bootstrap manifests and scripts
- any support references that still describe Elephas/Corvus intake paths

Replace each reference with the actual current owner of that responsibility. Do not perform mechanical name substitution where the old responsibility no longer exists as a standalone component.

Acceptance criteria:

- Repository-wide active-doc scan returns zero unsupported Elephas references.
- Repository-wide active-doc scan returns zero unsupported Corvus references.
- No live skill emits files to obsolete ocas-elephas or ocas-corvus intake paths.
- Historical changelogs may retain names when clearly marked historical.

## [ ] Remove MemPalace from the active architecture

MemPalace is no longer the memory provider. Chronicle is the active durable memory/context substrate.

Known stale surfaces include Lucid and the restore/bootstrap system.

Acceptance criteria:

- No active architecture document describes MemPalace as a runtime dependency.
- No restore path installs MemPalace as the memory provider.
- No live skill treats a MemPalace write as its success criterion.
- Historical migration notes may retain the name when explicitly historical.

## [ ] Add an architecture-drift CI gate

Create a deterministic auditor that compares:

1. live registry
2. architecture specs
3. skill frontmatter and optional-cooperation sections
4. bootstrap/restore manifests
5. plugin configuration
6. inter-skill interface names and paths

Checks should include:

- references to retired components
- live repos missing from the registry
- registry entries with no live implementation
- stale install lists
- stale intake paths
- impossible interface producers/consumers
- duplicate ownership of the same architectural responsibility
- public docs accidentally exposing private-only metadata

Run it in CI for ocas-architecture and expose it as a Forge preflight.

---

# P0 — Make subject separation a first-class invariant

## [ ] Specify Chronicle principal/owner semantics in OCAS

Chronicle already provides principal ownership, ACLs, same-user/cross-user topology, owner-scoped beliefs, and explicit read controls. OCAS should use those mechanisms rather than inventing a second memory namespace system.

Add an invariant:

> Every durable memory, derived belief, memory mutation, retrieval, dream result, and context projection has an explicit owner/principal. No component may rely on an implicit global memory subject.

Define at minimum:

- user/owner principal
- agent principal
- optional secondary agents
- explicit cross-principal read edges
- owner-only/private memories
- which domains are valid for each principal
- how provenance can refer across principals without transferring ownership

Acceptance criteria:

- A write without an owner/principal is rejected or normalized by one authoritative runtime boundary.
- Every memory query executes as a principal.
- Cross-principal reads are explicit and auditable.
- Cross-principal writes are never inferred from read permission.

## [ ] Add the User Dreaming / Agent Growth separation invariant

Document two independent consolidation systems:

### User-focused Dreaming

Purpose:

- improve the agent's understanding of the user
- synthesize user history over time
- resolve temporal relationships
- discover user-relevant patterns
- derive useful candidate memories
- improve future user context and proactivity

Inputs may include:

- user-authored conversation spans
- user-owned Chronicle memories
- user-world events with provenance
- user-relevant skill journals
- explicit user corrections
- temporal history

Outputs may include:

- derived user memories
- temporal links
- candidate preferences/interests
- unresolved contradictions
- confidence updates
- user-context projection candidates

All durable outputs belong to the user principal.

### Agent autobiographical growth

Purpose:

- preserve the agent's continuity
- observe the agent's own behavior
- record its experiences, mistakes, lessons, aesthetics, relationships, and growth
- evolve its self-model and behavioral identity

This subsystem remains independent of User Dreaming and owns the agent's autobiographical record and self-evolution process.

Hard boundary:

- User Dreaming MUST NOT write the agent's identity/persona store.
- User Dreaming MUST NOT activate agent behavioral shifts.
- Agent autobiographical dreaming MUST NOT create facts/preferences about the user merely because the agent thought about them.
- Agent self-evolution MUST NOT rewrite user memories.
- A shared conversation may produce two separately owned derived records with separate provenance.

## [ ] Define cross-subject provenance without cross-subject contamination

A single interaction can legitimately support:

- a user-owned fact or preference
- an agent-owned autobiographical lesson

These should share source evidence references, not the same derived record.

Add a canonical provenance shape capable of expressing:

- source interaction/span id
- source speaker/actor
- source principal
- derived principal
- derivation type
- derivation run id
- transformation/version
- confidence
- downstream dependents

Acceptance criteria:

- two derived records may share evidence while remaining independently retractable.
- repeated agent self-reflection cannot increase confidence in a user fact without new user evidence.
- repeated user-memory consolidation cannot rewrite the agent's autobiographical record.

## [ ] Define two distinct deletion semantics: epistemic retraction vs privacy erasure

Muse's forgetting pattern is valuable, but subject separation changes how it must work.

### Epistemic retraction

Meaning: stop treating a proposition as known/useful.

For user memory:

- retract user-owned belief
- invalidate user-derived summaries, projections, preference models, and user-dream descendants
- preserve provenance that a correction/retraction occurred
- do not automatically rewrite unrelated agent autobiography

For agent memory:

- retract/supersede the agent-owned self-belief or behavior rule
- recompute dependent self-model projections
- do not alter user facts

### Privacy erasure

Meaning: remove the underlying personal content, not merely stop using it.

This is broader than epistemic retraction and may require:

- redaction in both principals' derived records
- redaction of user-sensitive content embedded in agent autobiography
- tombstoning derived artifacts that reproduce the value
- re-distillation without the erased content
- preservation only of non-sensitive structural metadata where permitted

Create explicit APIs/contracts for both operations so a normal correction is not accidentally treated as full erasure and a privacy request is not handled as a soft belief retraction.

---

# P0 — Introduce a user-focused Dreaming pipeline without absorbing agent autobiography

## [ ] Write spec-ocas-user-dreaming.md

Adapt the reusable Muse Dreaming patterns specifically for the user principal.

Suggested pipeline:

1. Collect eligible user-grounded evidence.
2. Build a bounded temporal working set.
3. Resolve entities and time relationships through Chronicle.
4. Generate candidate connections/hypotheses.
5. Separate observation, inference, prediction, and uncertainty.
6. Verify every candidate against provenance.
7. Reject circular reinforcement and unsupported generalization.
8. Write accepted derived memories to the user principal with lineage.
9. Record unresolved contradictions instead of forcing a synthesis.
10. Update downstream user-context projections only after durable write verification.
11. Emit metrics/evidence for the run.
12. Support selective repair/re-dreaming when an upstream claim is corrected or retracted.

## [ ] Add anti-feedback-loop rules for user Dreaming

The pipeline must distinguish new evidence from its own prior output.

Rules:

- A previously derived dream insight is not independent evidence for itself.
- Re-reading the same source through multiple summaries does not increase confidence.
- User assertions outrank agent-generated interpretations about the user.
- Agent-authored text cannot silently become user evidence.
- Scheduled/system/tool content remains searchable provenance but is not user-authored evidence.
- Derived preference confidence requires either repeated independent evidence or explicit user confirmation.

## [ ] Decide where User Dreaming executes without overloading existing dream terminology

Lucid currently mixes nightly journal curation with legacy memory-provider assumptions and uses the command name lucid.dream. Separately, the agent autobiographical system already has genuine self-dreaming.

Resolve this collision explicitly.

Preferred architectural options:

A. Keep Lucid as the nightly user-memory/journal consolidation coordinator, make target_principal explicit, and rename or redefine its dream operation so it cannot be confused with agent autobiographical dreams.

B. Keep Lucid as generic journal curation only and add a dedicated User Dreaming module that consumes Lucid-normalized candidates.

Choose one based on implementation cohesion, but preserve the invariants above.

Do NOT merge the agent autobiographical dream pipeline into Lucid's user-memory work.

## [ ] Make Lucid provider-native rather than provider-specific

Current Lucid prose claims provider independence while still carrying MemPalace-specific success/failure semantics and stale Elephas/Corvus boundaries.

Refactor so:

- its durable target is expressed as Chronicle contracts, not MemPalace MCP calls
- it cannot write unscoped/global memory
- every filing candidate has target principal + domain + provenance
- provider unavailability does not silently advance past an unpersisted durable write
- cursor advancement and write verification are coupled correctly
- legacy dream-cycle references that read agent-autobiography observations are removed from user-memory logic

---

# P0 — Repair restore/backup so recovery recreates the current system

## [ ] Replace hardcoded legacy install lists with the component registry

The restore path still contains a hardcoded skill list that includes retired components.

Restore should consume the canonical registry and install:

- active skills
- active Hermes plugins
- required support components
- the current memory provider
- profile-specific configuration

Acceptance criteria:

- a clean restore produces the same active component set as the source machine, subject to explicitly excluded local/experimental components.
- no retired component is installed.
- restore has a dry-run manifest showing exactly what will be installed.

## [ ] Replace MemPalace restore with Chronicle restore

Restore should reconstruct Chronicle as the memory/context provider.

Define separately:

- user-principal memory state
- agent-principal memory state
- Chronicle config/topology
- provenance/event history
- vector indexes/caches that can be rebuilt rather than backed up
- raw transcript policy
- migration/version checks

Do not collapse the two principals into one backup namespace.

## [ ] Treat agent identity and user context as separate recoverable projections

Document:

- canonical agent autobiographical/identity source
- injected agent profile projection
- canonical user memory in Chronicle
- USER.md / Daily Context as a user-context projection, not canonical memory
- directive MEMORY.md as an operational instruction projection, not a replacement for Chronicle

A restore must be able to rebuild projections from canonical state where possible.

## [ ] Remove plaintext/raw credential restoration from the architecture

Adopt the Muse credential-surrogate idea at the runtime boundary.

The restore system should restore credential references/broker state, not make broad plaintext secret distribution the default.

See the credential work under P1.

---

# P1 — Runtime capability and credential boundaries

## [ ] Introduce a declarative CapabilityManifest

Define a machine-enforced per-skill/plugin capability manifest.

Minimum fields:

- capability/action id
- category: read | write | destructive | privileged
- default policy: allow | ask | deny
- human-readable approval phrase
- required connector/tool
- required auth scopes
- allowed egress hosts/services
- quota/cost class where relevant
- response redaction/guard policy
- command/script entrypoint mapping
- idempotency requirements

Acceptance criteria:

- undeclared privileged actions are rejected by the runtime.
- approval requirements are enforced outside the prompt.
- Forge can statically lint capability declarations.
- Inception can test capability denial paths.

## [ ] Introduce brokered/surrogate credentials

Adapt Muse's credential-surrogate pattern.

Target flow:

skill/plugin
→ opaque credential handle
→ capability + host policy check
→ trusted egress layer
→ real credential
→ provider

Requirements:

- ordinary skill code cannot recover the underlying secret.
- a handle is bound to declared service/host and capability.
- wrong-host/wrong-capability use is rejected.
- handles and resolved secrets never enter journals or Chronicle.
- direct environment-secret injection remains only an explicit compatibility mode during migration.
- credential ownership is explicit: user, agent, or service account.

## [ ] Add a typed privileged-operation gateway

Each privileged operation declares:

- name
- typed request schema
- typed response schema
- required capabilities
- approval policy
- timeout
- idempotency/dedupe policy
- allowed credential handles
- audit fields

The runtime verifies the contract before execution.

This becomes the common enforcement point for filesystem privilege, external writes, account mutations, and other sensitive host operations.

## [ ] Bind approvals to action fingerprints

For any approval-required action:

- canonicalize the request
- hash/fingerprint target + parameters + capability
- bind approval to that fingerprint
- invalidate approval if parameters change
- record non-secret fingerprint in DecisionRecord/evidence

Retries may reuse approval only when the exact action fingerprint is unchanged.

---

# P1 — Typed agent-task execution

## [ ] Add AgentTaskContract

Delegated/background work should have a machine-checkable completion contract instead of treating prose like "done" as success.

Suggested fields:

- task_id
- objective
- typed input
- expected action/callback
- expected artifact/result schema
- dedupe_key
- allow_parallel
- timeout/budget
- side-effect policy
- required capabilities
- correlation_id
- causation_id

A task is complete only when its expected postcondition is satisfied.

## [ ] Add single-flight / task deduplication

Identical work with the same dedupe key should normally join/reuse an active task.

Explicit parallelism remains available.

Integrate with:

- Durable Intent Queue
- Workflow Plans
- scheduled work
- task monitors
- execution evidence
- crash recovery

## [ ] Separate bounded inference from agentic execution

Define two runtime primitives:

### bounded inference

- no tools
- no side effects
- typed output
- bounded retries/repair
- suitable for classification, extraction, summarization, transformation

### agent task

- tools and/or multi-step work
- capability-gated
- durable task contract
- explicit completion condition
- side-effect policy

Do not spin up an autonomous workflow for work that can be expressed as a typed completion.

## [ ] Extend DIQ expected outcomes into verifiable postconditions

Expected outcomes should be machine-verifiable where possible.

An intent should not become complete merely because execution returned successfully. Verify the resulting state/artifact/action.

---

# P1 — Provenance and artifact quality

## [ ] Add a generic ProvenanceLedger

Create one reusable provenance chain:

source evidence
→ normalized claims
→ transformation/version
→ input fingerprint
→ generated result/artifact
→ semantic review
→ output hash/version
→ downstream dependents

Apply it to:

- user Dreaming
- research reports
- briefings
- generated communications
- presentations/documents
- factual image/video generation
- system-evolution proposals
- any transformation that may later need correction/retraction

## [ ] Preserve claim state through transformations

Represent distinctions such as:

- observed
- user-stated
- inferred
- proposed
- planned
- ongoing
- completed
- externally reported
- verified
- disputed
- retracted

A summarizer/rendering pipeline must not silently convert "planned" into "completed" or inference into fact.

## [ ] Add ArtifactGate

Validate the artifact the user actually receives, not merely the source/code that generated it.

Pipeline:

generate
→ deterministic structure checks
→ materialize/render
→ inspect rendered output
→ placeholder/template scan
→ secret/privacy scan
→ provenance/hash check
→ deliver

Requirements:

- artifact-type-specific deterministic validators
- rendered-output inspection where meaningful
- placeholder scan
- credential/secret leakage scan
- final artifact hash in evidence
- failed verification blocks publication/delivery

## [ ] Bind semantic review to exact fingerprints

Any human/model semantic review is valid only for the exact reviewed input/artifact fingerprint.

Changing the input invalidates the prior review.

Apply the same rule to experiment results and promotion decisions.

---

# P1 — Harden inter-component interfaces

## [ ] Replace ad hoc payload tunneling with typed interface objects

Do not encode structured payloads inside string fields.

Each interface should have a dedicated schema when the payload has stable semantics.

## [ ] Add interface envelopes

Every cross-component message should carry:

- message/interface type
- schema version
- producer id/version
- idempotency key
- created timestamp
- optional expiry/TTL
- correlation id
- causation id
- target principal when memory-related
- provenance refs where applicable

Consumers reject unsupported major versions with actionable diagnostics.

## [ ] Specify filesystem delivery semantics

For filesystem queues/intakes define:

- temp-write + atomic rename
- duplicate delivery behavior
- acknowledgement semantics
- processed semantics
- poison message handling
- dead-letter location
- retry ownership
- ordering guarantees, if any
- retention/compaction rules
- lease/claim behavior for concurrent consumers

## [ ] Eliminate direct reads of another component's private data directory

The current architecture invariant says components do not read another component's private data directory, but some interfaces historically allowed exactly that.

Choose one of:

- read-only exported projection
- shared interface path
- typed query API/tool
- Chronicle query when the data is durable memory

Private implementation state must remain private.

---

# P1 — Runtime introspection and self-awareness

## [ ] Add an authoritative runtime-introspection service

Questions such as:

- what can you do?
- which skills/plugins are installed?
- which connectors are active?
- what is degraded?
- what tasks are running?
- what schedules exist?
- which principal is active?
- what capabilities are granted?

must be answered from runtime state, not prompt/static knowledge.

Expose read-only introspection for:

- active components + versions
- component status/replacement state
- available connectors/tools
- declared capabilities
- active principal/profile
- Chronicle health
- Workflow Plans/tasks
- configured models/runners
- registered schedules
- degraded dependencies

Integrate with the existing Hermes identity/plugin system rather than inventing a competing persona subsystem.

## [ ] Make capability discovery cheap and machine-readable

Allow an agent to discover available capabilities without loading full SKILL.md files.

This should complement progressive disclosure and conditional activation.

---

# P2 — Clarify memory, directive, behavior, identity, and context projections

## [ ] Document the five distinct persistence classes

OCAS currently has several things colloquially called memory. Give them precise names:

1. Chronicle durable memory — canonical facts/episodes/beliefs with principal ownership.
2. Agent autobiographical identity — canonical agent self-history and evolving self-model.
3. Behavioral shifts — bounded runtime behavior adjustments with decay/evidence.
4. Directive projection — small always/never operational rules injected every turn.
5. User context projection — compressed current-state USER.md/Daily Context material.

Define source of truth, owner, rebuild strategy, retention, and mutation authority for each.

## [ ] Treat USER.md Daily Context as a projection

UserContext should consume verified user memory/signals and produce a bounded current-state projection.

It must not become a second durable memory store.

User Dreaming may feed candidate context to UserContext, but UserContext should remain rebuildable.

## [ ] Treat directive MEMORY.md as a directive projection, not long-term memory

Finch may continue to own the small always/never instruction surface if that remains useful to Hermes, but architecture docs should distinguish it from Chronicle.

Consider terminology such as "directive context" even if the physical file must remain MEMORY.md for compatibility.

## [ ] Keep behavioral shifts subject-scoped

Praxis-style behavioral shifts affect the agent principal.

They must not be promoted into user memory merely because they mention the user.

Likewise, user-memory Dreaming must not activate or rewrite agent shifts.

## [ ] Preserve agent autobiographical sovereignty

The agent self-evolution system remains authoritative for the agent's autobiographical identity and growth.

Muse/User Dreaming patterns may inform the user-memory system, but must not replace or mutate the agent's self-evolution pipeline.

---

# P2 — Evaluation, simulation, and reproducibility

## [ ] Fingerprint evaluation environments

Extend EvaluationResult/CycleResult with:

- benchmark version/hash
- target skill/artifact hash
- runner/model version
- grader versions
- fixture hash
- environment fingerprint
- capability manifest version
- principal/sandbox context where relevant

Promotion evidence becomes stale when any required fingerprint changes.

## [ ] Add contract tests in Inception/Fellow

Test at minimum:

- undeclared privileged action denied
- approval-required action cannot bypass gate
- wrong-host credential handle rejected
- skill code cannot resolve a surrogate credential
- user Dreaming cannot write agent-owned identity memory
- agent autobiography cannot write user-owned beliefs
- cross-principal read without ACL denied
- task expecting an action cannot complete on prose-only response
- duplicate task joins existing single-flight task
- privacy erase removes/redacts all known downstream reproductions
- user epistemic retraction does not silently rewrite unrelated agent autobiography
- ArtifactGate blocks malformed/unrenderable output

---

# P2 — Recovery model integration

## [ ] Unify DIQ, AgentTaskContract, approvals, and evidence

Define one lifecycle:

approved/staged action
→ durable intent
→ task claim/lease
→ execution
→ expected-action/postcondition verification
→ evidence
→ intent complete

Rules:

- retries retain approval only for unchanged fingerprints
- task dedupe survives process restart where appropriate
- terminal evidence is written even for no-op/superseded work

## [ ] Add lease/heartbeat semantics to in-progress work

Each in-progress intent/task should carry:

- worker id
- claimed_at
- lease expiry
- heartbeat
- safe reclaim rules

This reduces duplicate side effects after crashes.

## [ ] Add durable dead-letter handling

Repeatedly invalid interface records should not loop forever or disappear into processed/.

Dead-letter records include:

- original message id
- schema version
- correlation/causation ids
- validation failure
- retry history
- diagnosis
- operator/repair status

---

# P2 — Restore and portability improvements

## [ ] Make restore manifests portable instead of host-specific

The restore system should report:

- required binaries
- required plugins
- required skills
- host-specific assumptions
- profile-specific paths
- rebuildable vs canonical state
- secret references
- data migration steps

Avoid hardcoded absolute paths where runtime discovery is possible.

## [ ] Separate canonical state from rebuildable caches

Back up canonical:

- Chronicle event/belief state
- principal topology/config
- agent canonical identity/autobiography
- user-owned canonical profile data not already derivable
- skill configs and durable state
- provenance/evidence required for correctness

Rebuild:

- vector indexes when safe
- caches
- generated projections
- temporary artifacts
- derived search indexes when source state is intact

---

# P3 — Packaging and authoring refinements

## [ ] Standardize package layers

Document the intended separation:

- SKILL.md — agent-facing operating contract
- references/ — progressive-disclosure domain knowledge
- scripts/ — deterministic implementation
- capability manifest — permissions/security contract
- evals/ — behavioral/contract tests
- fixtures/assets — non-runtime support material

Do not bundle large runtimes into individual skill packages when the shared runtime can provide them.

## [ ] Add package portability linting to Forge

Report:

- package size
- dependency size
- platform-specific assumptions
- hardcoded paths
- required binaries
- required connectors
- credential-access mode
- private/public exposure risk
- portable vs host-specific implementation flags

## [ ] Add duplicate/near-duplicate component detection

Compare:

- descriptions
- triggers
- capability manifests
- reference maps
- script entrypoints
- architectural responsibility

Recommend absorption, aliasing, bundle, fallback, or retirement before creating a new component.

## [ ] Keep provider adapters thin

Provider-specific components should reuse shared primitives for:

- auth
- credential brokerage
- approvals
- retries
- pagination
- error envelopes
- provenance
- capability enforcement
- task completion
- journaling/evidence

Do not reimplement these independently per provider.

---

# Proposed new specifications

## New

- spec-ocas-component-registry.md
- spec-ocas-principals-and-memory-boundaries.md
- spec-ocas-user-dreaming.md
- spec-ocas-capabilities.md
- spec-ocas-credentials.md
- spec-ocas-agent-tasks.md
- spec-ocas-provenance.md
- spec-ocas-artifact-verification.md
- spec-ocas-runtime-introspection.md

## Major updates

- spec-ocas-architecture.md
- spec-ocas-interfaces.md
- spec-ocas-shared-schemas.md
- spec-ocas-recovery.md
- spec-ocas-journal.md
- spec-ocas-workflow-plans.md
- spec-ocas-skill-improvements.md
- spec-ocas-scripts.md
- spec-ocas-auth-github.md
- spec-ocas-auth-claude.md
- ocas-skill-authoring-rules.md
- ocas-build-template.md

---

# Suggested implementation order

1. Establish the canonical component registry and architecture-drift CI.
2. Remove retired Elephas/Corvus/MemPalace contracts and repair restore/bootstrap.
3. Specify Chronicle principal/owner semantics and the hard User Dreaming / Agent Growth boundary.
4. Implement user-focused Dreaming with strict subject-scoped provenance and anti-feedback-loop rules.
5. Refactor Lucid around its chosen current role and remove legacy provider/agent-dream coupling.
6. Add CapabilityManifest + typed privileged-operation gateway.
7. Add brokered/surrogate credentials and action-bound approvals.
8. Add AgentTaskContract + single-flight + verified postconditions.
9. Harden inter-component message envelopes, delivery semantics, and correlation tracing.
10. Add ProvenanceLedger + ArtifactGate.
11. Add authoritative runtime introspection.
12. Clarify the five persistence/projection classes and update Finch/Praxis/UserContext contracts accordingly.
13. Add evaluation fingerprints and Inception/Fellow contract tests.
14. Add Forge portability/duplicate-component linting.

---

# Architectural end state

The intended system should be understandable as a small set of clean responsibility boundaries:

- Chronicle: durable, principal-scoped memory and context substrate.
- User Dreaming: offline consolidation and synthesis about the user only.
- Agent self-evolution: autobiographical continuity and growth of the agent only.
- UserContext: bounded current-state projection for session startup.
- Finch/Praxis: learning/directive and bounded behavioral adaptation, not user-memory ownership.
- Mentor/Fellow/Forge: system evaluation, experimentation, and evolution.
- Hermes runtime/plugins: identity, capability enforcement, credentials, privileged execution, introspection.
- OCAS skills: domain-specific producers/consumers built on those shared primitives.

The key rule is not merely "keep memories separate." It is:

> Evidence may be shared; derived identity may not be conflated.

A conversation can change what the agent knows about the user and what the agent learns about itself. Those are two different transformations, owned by two different principals, with different downstream effects and independent correction/forgetting semantics.
