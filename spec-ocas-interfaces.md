# OCAS Inter-Component Interfaces

Spec Version: 2.0.0  
Author: Indigo Karasu

## Purpose

This specification defines supported communication between OCAS skills, Hermes runtime components, Chronicle, and system-evolution services. It replaces informal private-directory reads and legacy component-specific memory intake paths with typed contracts.

## Transport preference

Use the narrowest authoritative transport:

1. runtime/tool API for synchronous capability calls;
2. Chronicle contract for durable memory/context;
3. filesystem queue for asynchronous component handoff;
4. exported read-only projection for intentionally shared snapshots.

A component's private `commons/data/{component-id}/` directory is never an interface.

## Interface envelope

Every asynchronous filesystem message contains:

```json
{
  "message_id": "msg_<id>",
  "message_type": "<contract-name>",
  "schema_version": "1.0",
  "producer_id": "ocas-example",
  "producer_version": "1.2.3",
  "created_at": "ISO-8601",
  "expires_at": null,
  "idempotency_key": "<stable-key>",
  "correlation_id": "corr_<id>",
  "causation_id": "msg_<parent>|run_<parent>|null",
  "target_principal": null,
  "provenance_refs": [],
  "payload": {}
}
```

`target_principal` is REQUIRED for any message that can result in durable memory or identity mutation.

## Filesystem delivery

Consumer inbox:

```text
{agent_root}/commons/interfaces/{consumer-id}/inbox/{message_id}.json
```

Rules:

- producer writes a temporary file then atomically renames it;
- published messages are immutable;
- consumer deduplicates by `message_id` and `idempotency_key`;
- successful consumption moves/copies the message to `processed/` according to the consumer's retention policy;
- transient failures remain retryable with bounded attempts;
- invalid or retry-exhausted records go to `commons/dead-letter/{consumer-id}/` with diagnosis and retry history;
- unsupported major schema versions are rejected, not guessed;
- consumers own acknowledgement and retry state.

## Chronicle memory contract

Chronicle is the only durable memory/context substrate defined by OCAS architecture. OCAS skills do not write database files or route memory through a special memory-writer skill.

Every Chronicle write includes:

- acting principal;
- target/owner principal;
- memory domain/type;
- claim state (`user_stated`, `observed`, `inferred`, `planned`, `completed`, `disputed`, `retracted`, etc.);
- provenance references;
- confidence where applicable;
- derivation/run identifier for generated claims.

### User memory

User facts, preferences, interests, episodes and User Dreaming derivations target the **user principal**.

Agent-generated interpretation is never labeled user-stated. Re-reading the same evidence through multiple summaries does not create independent support.

### Agent memory/identity

Agent autobiographical observations, dreams, lessons and self-model changes target the **agent principal** and the agent identity subsystem's sanctioned stores/contracts.

They do not write user facts merely because the source interaction involved the user.

## User Dreaming contract

Input eligibility:

- user-owned Chronicle records;
- user-authored interaction spans;
- verified user-world events with provenance;
- explicit corrections/retractions;
- user-relevant journals that preserve source attribution.

Output:

- derived user memories;
- temporal links;
- contradiction records;
- confidence updates;
- projection candidates.

All durable output targets the user principal. User Dreaming MUST NOT mutate agent identity, agent autobiographical state, or agent behavioral shifts.

## Agent autobiographical growth contract

The agent-growth subsystem may consume agent behavior and shared interaction evidence. Its outputs are agent-owned autobiographical/identity records. It MUST NOT mutate user-owned Chronicle claims.

When one interaction feeds both User Dreaming and agent growth, each derived record has its own principal and provenance lineage.

## Journal feed

All skills write immutable journals under the journal root. Mentor, Lucid and other documented consumers may scan journals read-only while maintaining their own cursor state.

Journals are evidence. A journal consumer that proposes durable memory must use the Chronicle contract and set `target_principal` explicitly.

## Mentor -> Forge

Asynchronous `VariantProposal` and `VariantDecision` messages target `ocas-forge` via its interface inbox. They use the common envelope and schemas in `spec-ocas-shared-schemas.md`.

## Mentor -> Fellow

`ExperimentRequest` messages target `ocas-fellow`. Fellow is reactive unless separately configured; the request does not imply autonomous permission for external side effects.

## Fellow -> Mentor

Every experiment emits a `CycleResult` to Mentor, including abort/no-change outcomes. Results carry environment/artifact fingerprints so promotion evidence is bound to what was actually evaluated.

## Schedule/context -> Vesper

Schedule and briefing producers may emit typed briefing inputs to Vesper's inbox. Structured payloads MUST be represented as JSON objects in `payload`; do not JSON-encode structured data into prose/string fields.

## Vesper -> Dispatch

Delivery remains a typed session/runtime handoff unless an explicitly approved durable task contract is configured. Creating a queue entry does not grant permission to send a communication.

## Praxis -> Dispatch

Communication actions are proposals until Dispatch/runtime approval policy authorizes the concrete send. Approval is bound to the action fingerprint (recipient/target, content or content hash, account, capability and material parameters).

## Exported projections

A producer may publish a documented projection under:

```text
{agent_root}/commons/exports/{producer-id}/{projection}.json
```

Consumers may read only projections explicitly documented in their contracts. Missing/stale exports degrade gracefully. Private data directories and private databases are not projections.

## Cooperative runtime queries

Direct skill/runtime invocation is permitted when a typed capability exists (for example research enrichment). The caller must discover that the capability is available and degrade if optional.

## Correlation and causation

Multi-step work preserves:

- `correlation_id` across the end-to-end user/system operation;
- `causation_id` for the immediate triggering message/run;
- provenance references for factual lineage.

These IDs appear in journals, intents and evidence where applicable.

## Security boundary

An interface contract does not itself grant capability or credentials. Privileged operations are additionally subject to runtime capability/approval/credential policy. A consumer must reject a message requesting an operation it is not authorized to perform.

## Validation

A valid interface must define:

- producer and consumer;
- transport;
- schema and major version;
- idempotency semantics;
- acknowledgement/retry/dead-letter behavior for queues;
- target principal for memory/identity effects;
- side-effect/approval policy where relevant;
- provenance expectations for factual transformations.

Undocumented cross-component paths are architecture violations.
