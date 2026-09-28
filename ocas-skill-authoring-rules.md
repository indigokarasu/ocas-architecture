# OCAS Skill Authoring Rules

Version: 3.0.0
Author: Indigo Karasu
Status: normative

## Core rule

Build the smallest component that reliably owns one responsibility.

Before creating a skill, check components.json. If an active component already owns the responsibility, extend it or define a documented interface instead of creating overlap.

## Routing

A skill description is routing logic. It states what the skill does, when to use it, and nearby non-trigger cases.

Avoid branding-only descriptions and giant trigger lists.

## Responsibility boundary

Every workflow/system skill states:

- what it owns;
- what it does not own;
- which current component owns adjacent responsibility.

Do not name retired components as current owners.

## Package shape

Base:

~~~text
SKILL.md
README.md
CHANGELOG.md
~~~

Optional only when justified:

~~~text
references/
scripts/
assets/
evals/
capabilities.json
~~~

SKILL.md is the operational surface, not a changelog or knowledge dump.

## Storage

Private state belongs to the owner:

~~~text
{agent_root}/commons/data/{component-id}/
~~~

Journals:

~~~text
{agent_root}/commons/journals/{component-id}/YYYY-MM-DD/{run_id}.json
~~~

Cross-component filesystem communication uses documented interfaces/exports, never another component's private data directory.

## Interfaces

Prefer:

1. typed runtime/tool contract;
2. principal-scoped Chronicle contract for durable memory;
3. typed filesystem interface;
4. exported read-only projection.

Durable cross-component messages are versioned and idempotent.

Do not tunnel structured JSON through unrelated string fields.

## Memory

Chronicle is the durable memory/context substrate.

Memory mutation names the target principal explicitly.

User memory and agent memory are separate ownership domains.

User Dreaming writes only user-owned derived memory.

Agent autobiographical growth writes only agent-owned identity/autobiographical state.

Directive files and UserContext are projections, not Chronicle replacements.

## Journals

Every meaningful run writes an immutable journal.

A journal is evidence, not automatically durable memory.

Action journals record postcondition verification for side effects.

## Side effects and recovery

Scheduled/side-effecting skills implement:

- durable intent;
- idempotency/dedupe;
- claim/lease when concurrent;
- capability/approval policy;
- execution evidence;
- postcondition verification;
- repair re-validation;
- explicit no-op reason;
- degradation handling;
- dead-letter behavior for durable queues.

## Capabilities and credentials

Privileged operations should be machine-enforced where the host supports it.

A capability declaration identifies operation, policy, scopes, credential class, and schemas.

Prefer brokered/opaque credential handles to raw secret injection.

Never place secrets in journals, memory, interface messages, examples, or artifacts.

## Background tasks

Use the runtime scheduler rather than hardcoding a legacy scheduler CLI into architecture-level rules.

A skill with background work documents:

- stable job id/name;
- schedule/cadence;
- exact task contract;
- idempotent registration;
- gap detection;
- no-op evidence;
- catch-up policy.

A skill without background work does not invent cron work merely for self-update.

## Optional cooperation

Optional peers require a fallback.

If a peer is truly required for the responsibility to function, declare that dependency explicitly in components.json and the interface contract.

## Runtime discovery

Do not hardcode runtime availability of tools, connectors, models, schedules, principals, or capabilities when authoritative introspection exists.

## Evaluation

For evolvable skills:

- declarative evals;
- exact target/benchmark/runner/environment fingerprints;
- non-regression conditions;
- isolated side-effect policy;
- promotion tied to the exact evaluated artifact.

## Artifact-producing skills

Validate the delivered artifact, not only source code.

Use deterministic checks plus render/materialization inspection where meaningful.

## Anti-patterns

- duplicate responsibility;
- private-directory coupling;
- direct runtime-database access;
- ownerless/global memory writes;
- agent inference promoted as user-direct evidence;
- self-reinforcing derived memory;
- undocumented side effects;
- completion inferred only from tool exit;
- credentials in prose/state;
- JSON-in-string schema tunneling;
- stale hardcoded runtime/tool inventory;
- package/reference sprawl;
- incident logs copied into durable rules instead of generalized lessons.

## Required sections for system skills

- Responsibility Boundary
- When to Use / When NOT to Use
- Execution Loop
- Storage
- Interfaces
- Memory/Principal Behavior when applicable
- Journal Outputs
- Recovery Behavior
- Background Tasks when applicable
- Optional Cooperation
- Support File Map
- Validation

## Validation

Before release:

- registry ownership passes;
- routing tests pass;
- no retired dependencies;
- no cross-private-state reads;
- interface/schema versions valid;
- principal boundaries valid;
- capability/credential rules valid;
- recovery/postconditions tested;
- journals/evidence valid;
- secret scan passes;
- eval/non-regression passes where required.

Architecture-level changes must pass python scripts/validate_architecture.py.
