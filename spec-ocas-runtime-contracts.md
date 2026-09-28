# OCAS Runtime Contracts

Spec Version: 1.0.0
Author: Indigo Karasu
Status: normative direction

## Purpose

Define shared runtime contracts that should be enforced outside ordinary skill prose wherever Hermes supports them.

These contracts prevent every skill from reimplementing permissions, secrets, privileged execution, task completion, provenance, artifact verification, and runtime self-awareness independently.

## CapabilityManifest

Each privileged capability declares:

- capability_id;
- operation;
- category: read | write | destructive | privileged;
- default_policy: allow | ask | deny;
- approval phrase/description when ask;
- required connector/tool;
- required auth scopes;
- allowed egress hosts/services;
- quota/cost class when relevant;
- request schema;
- response schema;
- idempotency requirement.

Undeclared privileged operations should be denied by the runtime.

## Brokered credentials

Preferred flow:

~~~text
skill
  -> opaque credential handle
  -> capability + host policy
  -> trusted egress boundary
  -> real credential
  -> provider
~~~

Ordinary skill code should not recover the underlying secret.

Credential handles bind to:

- owner: user | agent | service;
- service;
- allowed host(s);
- allowed capability/operation;
- expiry/rotation metadata where applicable.

Credential values never enter journals, Chronicle beliefs, interfaces, or execution evidence.

## PrivilegedOperation

A privileged operation declares:

- operation;
- request/response schemas;
- capability id;
- approval policy;
- timeout;
- idempotency/dedupe policy;
- credential class;
- audit fields.

The gateway validates before side effects.

## Approval fingerprints

Approval-required actions bind approval to the canonical action fingerprint.

If target or material parameters change, approval is invalid.

Retries reuse approval only when the fingerprint is identical and approval remains valid.

## BoundedInferenceContract

Use bounded inference when work needs model reasoning but no tools/side effects.

Fields:

- objective;
- input schema;
- output schema;
- token/time budget;
- retry/repair limit;
- model class constraints when necessary.

Suitable for classification, extraction, normalization, summarization, and transformation.

## AgentTaskContract

Use an agent task for tool-using or multi-step work.

Fields are defined in spec-ocas-shared-schemas.md and include objective, typed input, postconditions, dedupe key, parallelism, timeout, required capabilities, approval fingerprint, correlation/causation, and principal context.

A task is not complete because the model said it completed. Postconditions must verify.

## Single-flight

Tasks with the same dedupe_key normally join/reuse active work.

Explicit parallelism requires allow_parallel=true.

Durable/side-effecting dedupe identity should survive process restart.

## ProvenanceLedger

Correctable transformations preserve:

- source refs;
- normalized claim refs;
- transform/version;
- input fingerprint;
- output/artifact;
- semantic review result;
- output hash/version;
- downstream dependents.

A semantic review is valid only for the exact reviewed fingerprint.

## ArtifactGate

Deliverable artifacts follow:

~~~text
generate
  -> structural validation
  -> materialize/render
  -> inspect rendered output where meaningful
  -> placeholder/template scan
  -> secret/privacy scan
  -> provenance/hash check
  -> deliver
~~~

A syntactically valid source file is not sufficient when the rendered artifact is broken.

## Runtime introspection

The runtime should expose authoritative read-only introspection for:

- active components/versions/status;
- installed tools/connectors;
- capability grants;
- active profile/principal;
- Chronicle health;
- active tasks/workflow plans;
- registered schedules;
- model/runtime identity;
- degraded dependencies.

Answers about current capability come from runtime state, not model lore.

## Recovery integration

Durable side-effecting work integrates with spec-ocas-recovery.md:

~~~text
capability/approval
  -> durable intent
  -> task claim/lease
  -> execution
  -> postcondition verification
  -> evidence
  -> complete
~~~

Retries preserve idempotency and approval only when the canonical action fingerprint is unchanged.
