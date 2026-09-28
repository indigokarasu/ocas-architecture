# OCAS Dreaming and Learning Boundary Map

Spec Version: 1.0.0  
Status: normative supplement  
Date: 2026-09-27

## Authority and scope

This specification supplements:

- `spec-ocas-architecture.md`;
- `spec-ocas-user-dreaming.md`;
- `spec-ocas-principals-and-memory-boundaries.md`;
- `spec-ocas-storage-conventions.md`.

If a rule here conflicts with one of those ownership or principal contracts,
the more specific existing contract wins.

The purpose of this document is to keep three learning loops from collapsing
into one another:

1. understanding the user;
2. understanding the agent's own evolving identity;
3. improving agent/system behavior and implementation.

A single interaction may provide evidence to all three loops. Their derived
records remain separate.

## Core invariant

A user-owned fact or relationship interpretation, an agent-owned
autobiographical insight, and a system-improvement lesson are different
epistemic objects.

Shared evidence does not transfer ownership.

## 1. User evidence and User Dreaming

Chronicle is the canonical principal-scoped durable memory/evidence substrate.

User Dreaming is the offline consolidation process defined by
`spec-ocas-user-dreaming.md`. It may derive stable preferences, temporal
relationships, recurring context, relationship patterns, contradictions,
interests, goals and projection hints from eligible user-grounded evidence.

Accepted durable User Dreaming results:

- belong to the user principal;
- preserve provenance to user-grounded evidence;
- are written through sanctioned Chronicle contracts;
- do not become agent identity;
- do not directly activate agent behavioral shifts.

Chronicle may also expose descriptive interaction-pattern evidence, such as
recurrent corrections or repeated requests, provided those patterns preserve
authoritative event references and remain descriptive rather than becoming
behavioral policy inside Chronicle.

## 2. Shared Dreaming kernel domains

A portable Dreaming implementation may share orchestration, evidence,
candidate, verification, temporal and gating machinery across domains. It must
not share derived state across principals or subjects.

Two staging domains are permitted:

### relationship

The `relationship` domain stages user-owned relationship interpretations.

Its subject is the user principal. It may consume Chronicle evidence and
descriptive interaction patterns. A promoted kernel candidate is still only a
staged/accepted derivation until it is durably committed through the User
Dreaming/Chronicle contract.

It is not a separate durable-memory authority and it does not directly activate
agent behavior.

Runtime relationship or user-context hints must be rebuildable projections from
verified user-owned state, not a second canonical relationship database.

### self

The `self` domain stages agent-owned reflection about the agent's own
behavior.

Its subject is the active agent principal. A promoted self candidate is
eligible evidence for the autobiographical growth system; it is not an
automatic identity edit.

Autobio/SOUL remains authoritative for agent identity evolution.

### Cross-domain rule

A candidate from one domain cannot be promoted by the other domain's kernel.
No relationship candidate may silently become a self claim, and no self
candidate may become user memory.

## 3. Agent autobiographical growth

Agent autobiographical growth owns the agent's continuity, self-observation,
dreams, mistakes, lessons, aesthetics, relationships and evolving self-model.

Autobio/SOUL remains the identity authority.

It may cite shared interaction evidence, but it:

- writes only agent-owned autobiographical/identity state;
- does not manufacture user facts from agent reflection;
- does not rewrite user-owned Chronicle memory;
- independently evaluates whether a self observation is durable enough to
  affect character files or SOUL.

A shared Dreaming self-domain gate may improve evidence quality, but it does
not replace Autobio's distillation/evolution gate.

## 4. System-improvement loop

Finch, Praxis, Mentor, Fellow and Forge operate on agent/system improvement,
not user identity.

- **Finch** discovers repeated corrections, failures, breakthroughs and methods
  relevant to agent/system improvement.
- **Praxis** turns supported agent/system patterns into bounded behavioral
  shifts.
- **Mentor** evaluates whether changes improve outcomes.
- **Fellow** performs controlled empirical evaluation where applicable.
- **Forge** creates or modifies skills/implementation when appropriate.

A user-specific correction must be scoped before transfer. If it is evidence
about this user's preference or relationship with the agent, it belongs in the
user/User-Dreaming path. It becomes a global Finch/Praxis rule only when
independent evidence supports that it is genuinely system-general.

## Allowed information flow

```
HERMES INTERACTIONS
        |
        v
   CHRONICLE
 user-principal evidence
        |
        v
   USER DREAMING
 relationship/user derivations
        |
        +----> Chronicle user-principal durable memory
        |
        `----> rebuildable user/relationship projections


AGENT BEHAVIOR + SHARED INTERACTION EVIDENCE
        |
        v
 SELF-DOMAIN DREAMING (optional staging/verification)
        |
        v
 AUTOBIO / AGENT GROWTH
        |
        v
 agent-principal identity / SOUL


SYSTEM OUTCOMES / JOURNALS
        |
        v
 FINCH -> PRAXIS -> MENTOR/FELLOW/FORGE
        |
        v
 bounded behavior / skill / implementation changes
```

There is no direct edge:

- User Dreaming -> agent identity;
- relationship candidate -> agent behavioral shift;
- self candidate -> user memory;
- Finch finding -> user model;
- Autobio/SOUL -> user-owned Chronicle belief.

## Write-target matrix

| Producer | User-principal Chronicle | Dreaming staging | Agent autobiography/SOUL | System shifts/skills |
|---|---:|---:|---:|---:|
| Chronicle capture/curation | yes | no | no | no |
| User Dreaming | yes, through Chronicle contract | relationship | no | no |
| Relationship kernel | no direct durable write | relationship | no | no |
| Self kernel | no | self | staged evidence only | no |
| Autobio/agent growth | no user-memory write | optional self input | yes | no |
| Finch | no user-model write | no | no | findings only |
| Praxis | no user-model write | no | no | yes |
| Mentor/Fellow/Forge | evaluation evidence only | no | no | yes |

## Storage and isolation

Dreaming candidate/run state is component-private process state, not canonical
memory. It follows the OCAS skill-state convention:

```
<hermes-home>/
  commons/
    data/
      dreaming/
        profiles/
          <profile_id>/
            principals/
              <subject_principal_id>/
                relationship.json
                self.json
```

The namespace is part of DreamStore identity, not merely a path convention.

Every read and write must validate:

1. the requested `profile_id` is the active Hermes profile;
2. the `subject_principal_id` is authorized for the requested domain;
3. relationship-domain state targets the current user principal;
4. self-domain state targets the active agent principal;
5. every Chronicle evidence reference is readable under Chronicle's normal ACL
   for the relevant principal.

A mismatch is a hard denial. There is no default-principal fallback and no
cross-principal enumeration.

Canonical durable user memory remains in Chronicle. Canonical agent identity
remains in the autobiographical system. Dreaming process state must not become
a competing source of truth.

## Runtime projections

Runtime context may combine separately labelled projections from multiple
owners:

- Chronicle recall;
- UserContext/current-state projection;
- verified user/relationship projection;
- SOUL/agent identity projection;
- Praxis active behavior shifts.

A projection is rebuildable context, not canonical memory.

Candidate, held or blocked Dreaming state is never injected. Relationship
projection is derived only from verified user-owned state. Self projection is
derived only through the agent identity/autobiographical authority.

## Lucid migration

Lucid's historical `lucid.dream` is a journal-curation workflow with legacy
MemPalace/Elephas-era dependencies. It is not the normative User Dreaming or
agent autobiographical growth process.

During migration:

1. keep the legacy curator operational only where still required;
2. do not add new user-memory or SOUL ownership to the legacy curator;
3. reusable cursoring, re-emergence, stale handling, duplicate avoidance and
   recovery mechanics may move into their current owners;
4. a shared `dreaming/` implementation may temporarily live in Lucid as
   implementation scaffolding, but its relationship outputs remain governed by
   User Dreaming/Chronicle and its self outputs by Autobio/SOUL;
5. retired MemPalace, Elephas and Corvus contracts must not reappear as active
   dependencies.

## Example: one correction, three valid derivations

User says:

> Stop asking me before every obvious next step.

The same event may support:

- **User Dreaming:** a user-owned relationship/preference candidate, with
  Chronicle provenance.
- **Finch/Praxis:** only if repeated evidence shows an agent/system-general
  confirmation problem.
- **Autobio:** an independent agent-owned observation such as a tendency to
  substitute permission-seeking for judgment.

Those records have separate principals, confidence, lifecycle and retraction
behavior. One does not automatically promote another.

## Security and trust

- User-model evidence must resolve to human-attributed source material.
- Automation, tool output, host control frames and the agent's own words are not
  user-direct evidence.
- A model-written quote is not authoritative evidence; verification reopens the
  referenced source.
- Prior Dreaming output is not independent support for itself.
- Cross-domain promotion is rejected rather than silently coerced.
- Secrets should remain in source systems; Dreaming process state should keep
  minimal references or redacted excerpts where possible.
- Privacy erasure follows the principal/memory-boundary contract and may trace
  downstream reproductions across projections and autobiography.

## Non-goals

This architecture does not make the shared Dreaming kernel:

- a replacement for Chronicle;
- a second canonical relationship database;
- a replacement for User Dreaming's durable-write contract;
- a replacement for Autobio/SOUL;
- a replacement for Finch/Praxis/Mentor/Fellow/Forge;
- an excuse to merge user and agent autobiographical state.
