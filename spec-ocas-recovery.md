# OCAS Recovery, Self-Diagnosis, and Self-Repair

Spec Version: 1.0.0
Author: Indigo Karasu
Status: normative

## Purpose

Scheduled and side-effecting work must survive interruption without duplicating effects or falsely reporting completion.

The recovery model combines:

1. Durable Intent Queue;
2. task claim/lease;
3. Execution Evidence Log;
4. self-diagnosis/repair;
5. postcondition re-validation.

## Durable Intent Queue

Every side-effecting action is staged before execution.

~~~json
{
  "intent_id": "intent_<id>",
  "created_at": "ISO-8601",
  "status": "staged",
  "action_type": "string",
  "action_fingerprint": "sha256:...",
  "principal_id": "string|null",
  "condition_snapshot": {},
  "expected_postconditions": ["string"],
  "dedupe_key": "string|null",
  "approval_ref": "string|null",
  "max_attempts": 10,
  "stale_threshold_hours": 72,
  "attempts": 0,
  "last_error": null,
  "superseded_by": null,
  "lease": null
}
~~~

## State machine

~~~text
staged -> in_progress -> verifying -> complete
staged -> superseded
staged -> cancelled
staged/in_progress -> stale
in_progress -> staged   (expired lease reclaimed safely)
verifying -> staged     (postcondition failed; retry allowed)
~~~

## Processing rules

1. Read unresolved intents before new work.
2. Re-evaluate condition_snapshot against current state.
3. Supersede intents whose motivating condition no longer holds.
4. Claim work with worker id and lease before execution.
5. Heartbeat long-running leases.
6. Execute only after capability/approval checks pass.
7. Move to verifying after the operation returns.
8. Verify expected_postconditions from resulting state.
9. Mark complete only after verification succeeds.
10. On retryable failure, increment attempts and return to staged.
11. Reclaim an expired lease only when idempotency rules make retry safe.
12. Mark stale only after attempt/age policy is exhausted and emit diagnosis.

## Action fingerprints and approval

Approval attaches to a canonical action fingerprint.

If target or material parameters change, prior approval is invalid.

Retries may reuse approval only when the fingerprint is identical and the approval is still valid.

## Dedupe and single-flight

dedupe_key prevents concurrent equivalent work.

When equivalent work is already active, callers reuse/join it unless the task contract explicitly permits parallel execution.

## Execution Evidence Log

Every scheduled run writes evidence, including deliberate no-op runs.

~~~json
{
  "run_id": "run_<id>",
  "timestamp": "ISO-8601",
  "component_id": "string",
  "status": "ok|error|skipped|degraded",
  "principal_id": "string|null",
  "correlation_id": "corr_<id>|null",
  "gap_detected": null,
  "intents_processed": 0,
  "intents_executed": 0,
  "intents_superseded": 0,
  "intents_stale": 0,
  "side_effects_executed": false,
  "postconditions_verified": true,
  "not_activity_reason": "string|null",
  "degraded_dependencies": [],
  "error": "string|null"
}
~~~

not_activity_reason is mandatory when no intended work occurred.

## Self-diagnosis

Failure classes:

- transient: retry likely sufficient;
- persistent: dependency/config/auth issue;
- structural: implementation/schema/logic bug;
- degraded: fallback path functioning with reduced capability.

Fixability:

- self-fixable;
- escalatable;
- behavioral (Praxis domain);
- structural/build (Forge domain).

## Repair protocol

1. collect evidence;
2. classify;
3. stage a repair intent if self-fixable;
4. execute repair;
5. rerun the failing validation/postcondition;
6. record success only if re-validation passes;
7. otherwise escalate with diagnosis.

## Schedule gap detection

Each scheduled run compares last successful evidence to expected cadence.

Guideline thresholds:

- interval N: gap > 2N;
- daily: gap > 36h;
- weekly: gap > 10.5d;
- multi-daily: gap > 2x expected interval.

Catch-up is bounded and oldest-first. If gaps suggest scheduler failure, verify scheduler registration/runtime health after catch-up.

## Dependency degradation

~~~text
primary
  -> secondary
  -> cache/local data
  -> explicit degraded/skip result
  -> escalation when critical or prolonged
~~~

Every fallback is visible in evidence.

## Data integrity

Before durable writes validate:

- schema/types;
- referential integrity where applicable;
- sanity/ranges;
- principal ownership for memory;
- capability/approval for privileged effects.

On read corruption:

- detect;
- recover from canonical/prior source when possible;
- verify;
- record;
- escalate if unrecoverable.

Append-only JSONL may truncate only an incomplete final line after interruption, with a repair decision recorded.

## Idempotency

Use:

- action fingerprints;
- external object ids;
- idempotency keys;
- dedupe keys;
- conditional query-before-write;
- provider idempotency tokens where available;
- merge/upsert semantics where safe.

Blind repeated side effects are prohibited.

## Dead-letter

Retry-exhausted durable interface messages move to dead-letter with:

- original message id;
- schema version;
- error/validation failure;
- retry history;
- correlation/causation ids;
- diagnosis;
- repair status.

Dead-letter is not success and not silent discard.

## Escalation

Escalation includes:

- severity;
- category;
- summary;
- diagnosis;
- evidence refs;
- auto-fix attempts/results;
- blocked postcondition;
- recommended next automated/system action.

Never report success while the required postcondition still fails.

## Compaction

Recovery logs may compact older terminal records while preserving:

- unresolved/stale intents;
- latest transition per intent;
- failure/repair lineage;
- correlation/causation chain;
- evidence required to prove completion;
- retention obligations.

## AgentTaskContract integration

A durable AgentTaskContract may be represented by one or more DIQ intents.

Common lifecycle:

~~~text
capability/approval
  -> durable intent
  -> task claim/lease
  -> execution
  -> postcondition verification
  -> evidence
  -> complete
~~~
