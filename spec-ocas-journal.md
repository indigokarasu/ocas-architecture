# OCAS Journals & Evaluation Specification

Spec Version: 2.0.0
Author: Indigo Karasu
Status: normative

## Purpose

Journals are immutable run evidence used for traceability, evaluation, recovery, and optional downstream curation.

A journal is not automatically durable personal memory.

## Journal types

### Observation

No external side effect occurred. Typical uses: analysis, discovery, monitoring, and local classification.

### Action

At least one external or durable side effect occurred or was attempted.

### Research

Structured multi-source research with source/provenance tracking.

A component chooses the type that best describes the run contract. A single invocation MAY emit multiple journals when phases have materially different semantics.

## Path

~~~text
{agent_root}/commons/journals/{component-id}/YYYY-MM-DD/{run_id}.json
~~~

Completed journals are immutable and written atomically.

## Run identity

Every journal includes:

- run_id;
- comparison_group_id when paired for evaluation;
- role: normal, champion, or challenger;
- component_id;
- component_version;
- journal_spec_version;
- journal_type;
- timestamp_start;
- timestamp_end;
- normalized_input_hash;
- principal_id when principal-scoped;
- correlation_id and causation_id when part of larger work.

See JournalEntry in spec-ocas-shared-schemas.md.

## Runtime telemetry

Capture enough runtime identity to reproduce or interpret evaluation:

- model/runtime id when material;
- host/runtime version;
- capability/tool-set version when material;
- active profile/principal;
- environment fingerprint for controlled experiments.

Never log credentials or secret values.

## Decision record

The journal records what the component decided or produced and the evidence refs supporting that decision.

Reasoning summaries are concise, user/audit-safe summaries, not hidden chain-of-thought.

## Actions and side effects

Action journals record each attempted side effect with:

- operation;
- target class;
- action fingerprint where applicable;
- approval reference/fingerprint when required;
- result;
- postcondition verification result.

A successful tool/process return is not sufficient proof that the intended state changed.

## Memory candidates

A journal MAY carry Signal, DerivedClaim, or memory-candidate payloads.

Rules:

- target/owner principal is mandatory for any durable-memory proposal;
- user-memory candidates preserve user-grounded evidence;
- agent/tool/system text is not silently promoted to user-direct evidence;
- agent-owned observations remain agent-owned;
- candidates remain proposals until accepted by Chronicle.

## Artifacts

Artifact-producing runs record:

- artifact id/ref;
- input fingerprint;
- final artifact hash;
- structural/render verification where applicable;
- semantic-review fingerprint where applicable.

## Champion/challenger evaluation

Champion and challenger runs share comparison_group_id and normalized input.

Challengers MUST NOT execute real external side effects unless an explicitly isolated/simulated environment permits them.

Promotion evidence binds to exact fingerprints for:

- target/champion;
- challenger;
- benchmark;
- runner;
- environment;
- reviewed artifact when applicable.

Changing one of those fingerprints invalidates stale promotion evidence.

## Universal evaluation dimensions

Evaluation systems may track:

- completion/postcondition success;
- correctness/quality;
- latency/cost;
- recovery behavior;
- schema conformance;
- capability/approval violations;
- principal-boundary violations;
- artifact verification failures.

Domain components add their own OKRs.

## Consumers

Evaluation and curation systems may read journals.

Consumers maintain their own cursors and MUST NOT edit producer journals.

A journal consumer that proposes durable memory uses the Chronicle contract and explicit target principal.

## Privacy and minimization

Do not journal:

- passwords, tokens, API keys;
- unnecessary raw personal content;
- raw private browsing history when a bounded derived signal suffices;
- large duplicated tool output when a stable source/artifact reference is enough.

## Recovery relationship

Every scheduled or side-effecting run also emits ExecutionEvidence under spec-ocas-recovery.md.

A supposedly complete run without its required journal/evidence is a verification failure.

## Validation

A journal validator checks:

- valid JournalEntry shape/version;
- timestamps and run id;
- principal_id when memory-related;
- no obvious secrets;
- postcondition result for declared side effects;
- challenger side-effect restrictions;
- fingerprint completeness when used for promotion.
