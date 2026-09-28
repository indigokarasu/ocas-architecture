# OCAS Skill Build Template

Version: 3.0.0
Author: Indigo Karasu
Status: normative

## Purpose

Implementation contract for building or materially revising an OCAS skill.

The output is an installable skill package, not a planning memo.

## Before building

1. Read components.json.
2. Confirm the responsibility is not already owned.
3. Read spec-ocas-architecture.md and spec-ocas-interfaces.md.
4. Decide whether the behavior belongs in a skill or shared runtime contract.
5. Identify principal/memory implications.
6. Identify privileged capabilities/credentials.
7. Identify durable side effects and recovery/postconditions.

## Skill identity

- Name: ocas-{skill}
- Version: semantic version
- Type: shortcut | workflow | system
- Visibility: public | private
- One-sentence responsibility

## Required base package

~~~text
ocas-{skill}/
  SKILL.md
  README.md
  CHANGELOG.md
~~~

Add only justified support:

~~~text
references/
scripts/
assets/
evals/
capabilities.json
~~~

capabilities.json is required when the skill requests privileged/destructive writes, external account mutation, or brokered credentials.

## SKILL.md requirements

Every skill defines:

- when to use / when not to use;
- responsibility boundary;
- first useful action;
- workflow where relevant;
- failure/degraded behavior;
- storage;
- journals;
- interfaces;
- background tasks when any;
- support-file map when any.

## Storage

Private state:

~~~text
{agent_root}/commons/data/ocas-{skill}/
~~~

Journals:

~~~text
{agent_root}/commons/journals/ocas-{skill}/YYYY-MM-DD/{run_id}.json
~~~

Cross-component interfaces:

~~~text
{agent_root}/commons/interfaces/{consumer}/
{agent_root}/commons/exports/{producer}/
~~~

Never use another component's private state/database as an informal API.

## Memory and principals

A durable-memory proposal uses Chronicle's sanctioned contract and explicit target principal.

It records:

- target principal;
- source actor/speaker;
- evidence/provenance;
- claim/derivation type;
- confidence/temporal validity where relevant.

User Dreaming and agent autobiographical growth are separate write domains.

See spec-ocas-principals-and-memory-boundaries.md and spec-ocas-user-dreaming.md.

## Interfaces

Cross-component payloads use InterfaceEnvelope plus typed payload.

Do not:

- add undocumented private-directory reads;
- tunnel JSON through arbitrary strings;
- write runtime databases directly;
- introduce a retired dependency.

## Privileged capabilities

For each privileged operation declare:

- capability id;
- operation;
- category;
- default policy;
- approval requirement;
- required connector/tool;
- auth scope/credential class;
- allowed egress service/host if relevant;
- request/response schema;
- idempotency rule.

See spec-ocas-runtime-contracts.md.

## Credentials

Prefer opaque/brokered credential handles where supported.

Never write credential values into skills, journals, interfaces, Chronicle, evidence, or generated artifacts.

## Recovery

Every scheduled or side-effecting workflow implements spec-ocas-recovery.md.

Minimum:

- durable intent before effect;
- idempotency/dedupe;
- claim/lease when concurrent;
- evidence every run;
- explicit no-op reason;
- expected postconditions;
- re-validation before success;
- degradation/fallback;
- schedule gap detection;
- dead-letter handling for durable queues.

## Journals

Every meaningful run writes JournalEntry v2.

Action runs record postcondition verification, not only tool/process success.

Memory-related runs include principal context.

## Artifacts

If the skill creates user-deliverable artifacts, define an ArtifactGate appropriate to the artifact type:

generate -> structural validation -> render/materialize -> inspect -> placeholder/secret scan -> hash/provenance -> deliver.

## Evaluation

Evolvable skills SHOULD ship declarative evals.

Promotion evidence binds to exact target, benchmark, runner, environment, and artifact fingerprints.

Challengers cannot execute real external side effects unless isolated simulation explicitly permits them.

## Runtime introspection

Do not hardcode claims about currently installed tools/connectors/models when the runtime can introspect them.

Discover at execution time and degrade honestly.

## Validation checklist

- [ ] ownership checked against components.json
- [ ] no retired dependency
- [ ] routing tests pass
- [ ] package structure valid
- [ ] private storage boundaries valid
- [ ] interfaces typed/versioned
- [ ] memory writes principal-scoped
- [ ] capability/credential rules defined
- [ ] recovery/postconditions implemented
- [ ] journal valid
- [ ] artifact gate defined when needed
- [ ] evaluation fingerprints defined when evaluated
- [ ] no secrets/placeholders
- [ ] README/CHANGELOG updated

## Reference specs

- spec-ocas-architecture.md
- components.json
- spec-ocas-principals-and-memory-boundaries.md
- spec-ocas-user-dreaming.md
- spec-ocas-runtime-contracts.md
- spec-ocas-storage-conventions.md
- spec-ocas-interfaces.md
- spec-ocas-shared-schemas.md
- spec-ocas-journal.md
- spec-ocas-recovery.md
- spec-ocas-workflow-plans.md
- spec-ocas-skill-improvements.md
- spec-ocas-scripts.md
- spec-ocas-skill-publishing.md
- ocas-skill-authoring-rules.md
