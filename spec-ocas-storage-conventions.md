# OCAS Storage Conventions

Spec Version: 2.0.0  
Author: Indigo Karasu

## Purpose

This specification separates component-private state, immutable journals, cross-component interfaces, exported projections, and runtime-owned databases. Filesystem reachability is not an access contract.

## Roots

```text
{agent_root}/commons/
  data/{component-id}/       # component-private mutable/append-only state
  journals/{component-id}/   # immutable run journals
  interfaces/{component-id}/ # documented inbound/outbound queue surfaces
  exports/{component-id}/    # documented read-only projections
  dead-letter/{component-id}/# invalid/exhausted interface records
```

Runtime providers may maintain storage outside these roots. In particular, Chronicle storage is Chronicle-owned and MUST be accessed through Chronicle APIs/tools/contracts rather than by opening its database files.

## Private component state

`data/{component-id}/` is owned exclusively by that component.

Typical contents:

```text
config.json
*.jsonl
reports/
artifacts/
staging/
```

Other components MUST NOT read or write this directory directly. If data is intended for another component, expose it through an interface, an exported projection, or an authoritative runtime query contract.

## Journals

```text
{agent_root}/commons/journals/{component-id}/YYYY-MM-DD/{run_id}.json
```

Rules:

- one immutable file per completed run;
- write atomically via temporary file then rename;
- never edit a completed journal;
- journals are telemetry/evidence, not automatically durable memory;
- consumers track their own cursors/ingestion state rather than mutating producer journals.

## Interfaces

Inbound filesystem queues live at:

```text
{agent_root}/commons/interfaces/{consumer-id}/inbox/
{agent_root}/commons/interfaces/{consumer-id}/processed/
```

Invalid or retry-exhausted messages move to:

```text
{agent_root}/commons/dead-letter/{consumer-id}/
```

An interface message is immutable after publication. Producers write to a temporary filename in the inbox filesystem and atomically rename to the final `{message_id}.json`.

Every message carries the envelope defined in `spec-ocas-interfaces.md`, including schema version, producer, idempotency key, correlation id, causation id and target principal when memory-related.

## Exported projections

A component may deliberately expose a stable read-only projection:

```text
{agent_root}/commons/exports/{component-id}/{projection-name}.json
```

An export is not the component's private state. The producer owns its schema and refresh semantics. Consumers treat it as read-only and tolerate absence/staleness according to the documented interface.

## Chronicle

Chronicle is the durable memory/context provider. OCAS does not prescribe Chronicle's internal database layout.

Rules:

- no skill opens Chronicle database files directly;
- every durable memory operation executes as an explicit principal;
- user and agent records remain separately owned even when they cite the same evidence;
- provenance/event history required for retraction is canonical; rebuildable indexes/caches need not be treated as canonical backups;
- UserContext, directive files and other injected context are projections rather than Chronicle replacements.

## Config

Every component-local `config.json` includes at minimum:

- `component_id`
- `component_version`
- `config_version`
- `created_at`
- `updated_at`

Configuration is mutable state. Changes that affect external behavior should be auditable through DecisionRecord/evidence where practical.

## JSONL logs

Append-only JSONL records include a stable `id` and ISO-8601 timestamp. Mid-write recovery may truncate only an incomplete final line and must record that repair.

Common logs include:

- `decisions.jsonl`
- `intents.jsonl`
- `evidence.jsonl`
- domain-specific event logs

## Retention

Retention is explicit. Components do not silently delete canonical records. Log compaction preserves required audit/provenance semantics. Derived caches and projections may be rebuilt and have shorter retention than canonical evidence.

## Cross-component access

Allowed:

- sanctioned Chronicle contracts;
- typed runtime/tool contracts;
- documented filesystem interface queues;
- documented exported projections.

Forbidden:

- opening another component's `data/` directory as an informal API;
- opening another component's private database directly;
- writing into another component's journal tree;
- depending on an undocumented absolute host path.

## Initialization

A component creates only the roots it owns or consumes:

1. its private `data/{component-id}/` root;
2. its journal root;
3. its inbound interface root if it consumes filesystem messages;
4. its export root if it publishes projections;
5. its dead-letter root if it consumes filesystem messages.

Initialization is idempotent and logged.

## Validation

Validation checks:

- owned roots exist when required;
- config schema is valid;
- JSONL parses;
- journal writes are atomic/immutable;
- no undocumented cross-component private-state reads exist;
- interface messages conform to envelope/schema requirements;
- memory operations name a target principal;
- retention/compaction preserves required provenance.
