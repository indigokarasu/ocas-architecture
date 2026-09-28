# OCAS Shared Schemas

Spec Version: 2.0.0  
Author: Indigo Karasu

These are logical schemas. Implementations may add domain fields but MUST preserve the ownership, provenance, idempotency and correlation semantics below.

## InterfaceEnvelope

```json
{
  "message_id": "msg_<id>",
  "message_type": "string",
  "schema_version": "1.0",
  "producer_id": "string",
  "producer_version": "string",
  "created_at": "ISO-8601",
  "expires_at": null,
  "idempotency_key": "string",
  "correlation_id": "corr_<id>",
  "causation_id": null,
  "target_principal": null,
  "provenance_refs": [],
  "payload": {}
}
```

`target_principal` is required whenever processing can create/mutate durable memory or identity.

## ProvenanceRef

```json
{
  "ref_id": "prov_<id>",
  "source_type": "interaction|journal|memory|artifact|external_source|event",
  "source_id": "string",
  "source_principal": "string|null",
  "source_actor": "user|agent|system|external|null",
  "observed_at": "ISO-8601|null",
  "content_hash": "sha256:<hex>|null"
}
```

## DerivedClaim

```json
{
  "claim_id": "claim_<id>",
  "owner_principal": "string",
  "claim_type": "fact|episode|preference|interest|relationship|lesson|identity|other",
  "claim_state": "user_stated|observed|inferred|predicted|planned|ongoing|completed|reported|verified|disputed|retracted",
  "content": {},
  "confidence": 0.0,
  "provenance_refs": ["prov_<id>"],
  "derivation": {
    "type": "direct|user_dream|agent_reflection|research|other",
    "run_id": "run_<id>",
    "version": "string"
  },
  "created_at": "ISO-8601",
  "supersedes": null
}
```

Rules:

- agent interpretation about a user is `inferred`, never `user_stated`;
- repeated transformations of identical provenance do not increase evidence count;
- `owner_principal` is immutable; changing ownership creates a new record with explicit provenance.

## Signal

```json
{
  "signal_id": "sig_<id>",
  "timestamp": "ISO-8601",
  "source_component": "string",
  "target_principal": "string|null",
  "signal_type": "string",
  "payload": {},
  "confidence": "high|med|low|null",
  "provenance_refs": [],
  "correlation_id": "corr_<id>|null"
}
```

Signals are observations/proposals. A Signal is not durable personal memory merely because it exists.

## DecisionRecord

```json
{
  "decision_id": "dec_<id>",
  "timestamp": "ISO-8601",
  "component_id": "string",
  "decision_type": "string",
  "decision": "string",
  "reason": "string",
  "evidence_refs": [],
  "correlation_id": "corr_<id>|null",
  "action_fingerprint": "sha256:<hex>|null"
}
```

## DurableIntent

```json
{
  "intent_id": "intent_<id>",
  "created_at": "ISO-8601",
  "status": "staged|in_progress|complete|superseded|stale|cancelled",
  "action_type": "string",
  "target": {},
  "action_fingerprint": "sha256:<hex>",
  "expected_postconditions": [],
  "idempotency_key": "string",
  "correlation_id": "corr_<id>",
  "approval_ref": null,
  "attempts": 0,
  "max_attempts": 10,
  "lease": null,
  "last_error": null
}
```

Completion requires verified postconditions, not merely a successful function return.

## ExecutionEvidence

```json
{
  "run_id": "run_<id>",
  "timestamp": "ISO-8601",
  "component_id": "string",
  "status": "ok|error|skipped|degraded",
  "correlation_id": "corr_<id>|null",
  "intents_processed": 0,
  "side_effects_executed": false,
  "postconditions_verified": false,
  "not_activity_reason": null,
  "error": null,
  "artifact_hashes": []
}
```

## AgentTaskContract

```json
{
  "task_id": "task_<id>",
  "objective": "string",
  "input": {},
  "expected_result_schema": {},
  "expected_postconditions": [],
  "dedupe_key": "string",
  "allow_parallel": false,
  "timeout_seconds": 900,
  "side_effect_policy": "none|declared|approval_required",
  "required_capabilities": [],
  "correlation_id": "corr_<id>",
  "causation_id": null
}
```

## VariantProposal

```json
{
  "proposal_id": "prop_<id>",
  "target_component": "string",
  "base_version": "string",
  "observed_problem": "string",
  "supporting_evidence": [],
  "proposed_changes": "string",
  "evaluation_plan": "string",
  "environment_fingerprint": "sha256:<hex>|null"
}
```

## ExperimentRequest

```json
{
  "experiment_id": "exp_<id>",
  "target_component": "string",
  "target_hash": "sha256:<hex>",
  "benchmark_hash": "sha256:<hex>",
  "environment_fingerprint": "sha256:<hex>",
  "runner_version": "string",
  "constraints": {},
  "correlation_id": "corr_<id>"
}
```

## CycleResult

```json
{
  "cycle_id": "cyc_<id>",
  "experiment_id": "exp_<id>",
  "decision": "promote|no_change|abort",
  "baseline_score": 0.0,
  "best_variant_score": null,
  "target_hash": "sha256:<hex>",
  "benchmark_hash": "sha256:<hex>",
  "environment_fingerprint": "sha256:<hex>",
  "artifact_hash": "sha256:<hex>|null",
  "abort_reason": null
}
```

Promotion evidence is stale if the target, benchmark, environment or reviewed artifact fingerprint changes.

## ConfigBase

```json
{
  "component_id": "string",
  "component_version": "string",
  "config_version": "string",
  "created_at": "ISO-8601",
  "updated_at": "ISO-8601"
}
```

## Extension rules

Domain schemas may extend these objects but MUST NOT:

- remove principal ownership from memory-affecting records;
- tunnel structured payloads through prose strings;
- discard correlation/causation IDs in multi-step workflows;
- reinterpret an inference as a user-stated/verified fact;
- treat a journal/signal as automatically promoted durable memory;
- mark an intent complete without checking declared postconditions.
