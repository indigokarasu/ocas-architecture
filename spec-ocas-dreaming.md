# OCAS Dreaming and Learning Boundaries

Status: normative architecture  
Date: 2026-09-27

## Purpose

OCAS has three different kinds of learning that must not collapse into one
memory or promotion path:

1. learning descriptive facts and recurrent behavior about the user;
2. learning how this agent should relate to that user;
3. learning who the agent is becoming and how the system itself should improve.

The same interaction can produce evidence for all three, but each conclusion
has a different owner, scope, retention policy, and promotion gate.

This specification defines those ownership boundaries.

## Core invariant

A fact about the user, a relationship adaptation, a system improvement, and a
claim about the agent's identity are different epistemic objects.

No component may promote one into another merely because the text sounds
similar.

## The three learning loops

### 1. User/world evidence loop — Chronicle

Chronicle is the canonical evidence and memory layer.

It owns:

- durable interaction events and source provenance;
- speaker attribution and principal ownership;
- factual/episodic/semantic memory;
- contradictions, confidence and retrieval;
- descriptive recurrent interaction-pattern mining.

Chronicle may say:

> User messages repeatedly reject unnecessary confirmation in comparable
> interactions. Support: 7 events across 4 sessions.

Chronicle must not turn that observation into:

> Always proceed without asking.

The latter is behavioral policy and belongs to relationship Dreaming.

Chronicle interaction patterns therefore carry `scope: descriptive_only` and
authoritative event ids.

### 2. Relationship-learning loop — Dreaming relationship domain

Relationship Dreaming owns the evolving posture between a user and an agent.

It asks questions such as:

- What produces trust or friction with this user?
- Which behavior is stable versus task-specific?
- Was a correction about verbosity, sequencing, initiative, fidelity,
  uncertainty or something else?
- What should the agent try differently next time?
- Did the adaptation improve later interactions?
- Is the lesson strong enough to become a default for this relationship?

Its inputs are evidence references, primarily Chronicle events and Chronicle
descriptive interaction patterns.

Its outputs are scoped relationship claims/posture. These are neither Chronicle
facts nor SOUL identity.

The relationship domain uses candidate -> verify -> gate -> promote semantics.
`hold` and `block` may never change live posture.

### 3. Agent-self and system-evolution loops

These are deliberately split again.

#### Autobio / SOUL — agent identity

Autobio owns the agent's living self-portrait and identity evolution.

Inputs include actual agent behavior, Autobio observations, journals, external
feedback, dream interpretation, principle grades and prior character state.

The shared Dreaming kernel may stage and gate `self`-domain insights, but
promotion inside Dreaming only makes an insight eligible for Autobio
distillation. It does not edit SOUL.

Autobio remains the sole authority for Entity-tier changes:

- character files;
- canonical SOUL;
- profile SOUL projection.

The existing identity framing contract remains load-bearing: Indigo is distinct
from Jared; relationship conclusions cannot silently become Indigo identity.

#### Finch / Praxis / Mentor / Forge — system improvement

The system-improvement chain owns implementation and behavior of the agent
system itself:

- Finch discovers repeated corrections, failures, breakthroughs and methods
  relevant to agent/system improvement.
- Praxis turns supported agent/system patterns into bounded behavioral shifts.
- Mentor evaluates whether variants improve outcomes.
- Forge creates or changes skills/implementation when appropriate.

This loop may consume the same interaction event as Relationship Dreaming but
must not infer a user profile from it.

## Shared Dreaming kernel

The portable Dreaming machinery is shared implementation, not shared state.

During migration it lives under Lucid's `dreaming/` package.

Required domains:

- `relationship`
- `self`

Each domain has an independent namespace, candidate set, promoted set and
projection. Cross-domain promotion is an error.

The kernel owns generic mechanics:

- candidate identity;
- evidence references;
- staging;
- gate-before-promotion;
- namespace separation;
- temporal lifecycle primitives;
- grounding/preservation verification as those V2 components are migrated;
- model-provider abstraction;
- run/scheduler/state machinery.

Domain-specific code owns interpretation.

## Allowed information flow

```
                         CHRONICLE
             events / facts / provenance / patterns
                    │                 │
                    │                 └─────────────────────┐
                    ▼                                       ▼
          RELATIONSHIP DREAMING                       FINCH / PRAXIS
       user-agent relational posture                system improvement
                    │                                       │
                    ▼                                       ▼
             runtime projection                        behavior/skills

INDIGO BEHAVIOR / AUTOBIO RECORD
                    │
                    ▼
            SELF-DOMAIN DREAMING
        grounded staged self insights
                    │
                    ▼
             AUTOBIO DISTILLATION
                    │
                    ▼
                    SOUL
```

Relationship Dreaming has no Chronicle write path. Effects of a promoted posture
become new Chronicle evidence only when they participate in an ordinary Hermes
interaction and Chronicle captures that interaction through its normal turn/event
capture path.

There is no direct edge:

- Chronicle pattern -> SOUL
- relationship posture -> SOUL
- relationship posture -> Chronicle fact/event write
- self insight -> user model
- Finch finding -> user model

A component may create a new, independently grounded observation in another
loop, but it must pass that loop's own evidence and promotion rules.

## Write-target matrix

| Producer | Chronicle evidence | Relationship state | Autobio record | SOUL | System shifts/skills |
|---|---:|---:|---:|---:|---:|
| Chronicle | yes | no | no | no | no |
| Relationship Dreaming | read event refs only; no writes | yes | no | no | no |
| Autobio | optional evidence refs | no | yes | yes, through distillation | no |
| Self Dreaming | no | no | staged insight only | no | no |
| Finch | optional system evidence refs | no | no | no | findings only |
| Praxis | optional outcome refs | no | no | no | yes |
| Mentor | evaluation evidence | no | no | no | decisions |
| Forge | implementation evidence | no | no | no | yes |

## Storage

Recommended profile- and principal-scoped layout:

```
<hermes-home>/
  commons/
    db/
      chronicle/
        chronicle.db
    data/
      dreaming/
        profiles/
          <profile_id>/
            principals/
              <subject_principal_id>/
                relationship.json
                self.json
  profiles/<agent>/
    memories/
      USER.md               # user/context projection; not Dreaming source of truth
    SOUL.md                 # Autobio projection; not relationship state
```

`commons/data/dreaming` follows the OCAS skill-state storage convention;
`commons/db` remains reserved for database-backed shared subsystems such as
Chronicle.

The namespace is part of DreamStore identity, not just a directory convention.
Every read and write must validate both `profile_id` and
`subject_principal_id` against the active Hermes scope before opening state.
For the relationship domain, the subject principal is the current user
principal. For the self domain, it is the active agent principal. A mismatch is
a hard denial: there is no default-principal fallback and no cross-principal
enumeration.

Every Chronicle evidence reference used by a Dreaming candidate must also pass
Chronicle's normal principal/ACL read check for that same relationship scope.
A caller that cannot read the evidence cannot use it to read, stage, promote, or
project the derived Dreaming state.

Chronicle remains the authoritative source for original interaction evidence.
Dreaming stores evidence references rather than copied transcripts wherever
possible.

## Runtime projections

The active Hermes context may contain projections from several owners:

- Chronicle recall — what is relevant/known;
- UserContext — what is happening now;
- relationship Dreaming — how to work with this user;
- SOUL — who the agent is;
- Praxis runtime brief — bounded active system behavior shifts.

The projections must remain separately labelled internally even if the final
prompt assembler renders them adjacent to one another.

Dreaming relationship projection must be built from promoted relationship state
only. Candidate/held/blocked state is never injected.

## Example: one correction, four valid conclusions

User says:

> Stop asking me before every obvious next step.

Chronicle may record:

- the exact event;
- a direct-correction observation;
- after recurrence, a descriptive initiative/confirmation pattern.

Relationship Dreaming may conclude:

- with this user, proceed on obvious reversible next steps unless risk or
  ambiguity makes confirmation necessary.

Finch/Praxis may independently conclude:

- several OCAS workflows contain unnecessary confirmation gates;
- test a bounded change to those workflows.

Autobio may independently observe:

- I sometimes substitute permission-seeking for judgment.

SOUL changes only if that final self-observation becomes a durable agent trait
under Autobio's own evidence threshold. The relationship conclusion alone is
insufficient.

## Lucid migration

Lucid's historical `lucid.dream` is a journal curator built around MemPalace.
That responsibility is not the new Dreaming architecture.

Migration rule:

1. keep the legacy curator operational while consumers are moved;
2. do not add new user-model or SOUL mutation responsibilities to it;
3. migrate reusable mechanics (cursoring, re-emergence, stale handling,
   duplicate avoidance, recovery) to the owning systems;
4. use Lucid's new `dreaming/` package as the shared kernel during this
   transition;
5. once legacy MemPalace-dependent filing has no consumers, remove the curator
   surface or archive it.

## Scheduling

Recommended cadence:

- Chronicle capture: every completed turn.
- Chronicle descriptive-pattern mining: bounded incremental pass, suitable for
  nightly Dreaming input and optional lightweight periodic refresh.
- Relationship Dreaming: nightly, plus explicit/manual repair when needed.
- Autobio self observation: existing daily schedule.
- Self Dreaming verification/staging: after daily observation or before
  micro-distillation.
- Autobio identity distillation: existing daily/weekly cadence.
- Finch/Praxis/Mentor/Forge: existing system-improvement cadences.

Scheduling does not change ownership. A nightly job does not become "Dreaming"
merely because it runs at night.

## Security and trust

- User-model evidence must resolve to human-attributed source material.
- Automation, tool output, host control frames and the agent's own words are not
  evidence about the user.
- Principal/ACL boundaries in Chronicle remain authoritative.
- A model-written quote is not authoritative evidence; verifiers reopen the
  referenced source.
- No relationship or self candidate may promote without evidence.
- Cross-domain promotion is rejected, not silently coerced.
- Relationship and self stores must be profile/principal scoped, with scope checked on every read and write.
- Secrets should remain in source systems with redacted/hashed references in
  Dreaming state where possible.

## Non-goals

This architecture does not make Dreaming:

- a second general-purpose memory database;
- a replacement for Chronicle;
- a replacement for Autobio;
- a replacement for Finch/Praxis/Mentor/Forge;
- a new owner of USER.md;
- a reason to merge Jared and Indigo into one autobiographical state.
