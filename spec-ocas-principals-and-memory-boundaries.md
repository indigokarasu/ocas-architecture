# OCAS Principals and Memory Boundaries

Spec Version: 1.0.0  
Author: Indigo Karasu

## Purpose

Define ownership, derivation, retrieval, correction and erasure semantics for personal memory and agent identity. Chronicle supplies the durable principal/ACL substrate; OCAS components must preserve these boundaries.

## Principals

### user principal

Owns durable claims about the owner/user: stated facts, preferences, interests, episodes, relationships, corrections and derived user understanding.

### agent principal

Owns the agent's autobiographical experiences, self-observations, lessons, identity development and agent-owned operational history.

A deployment may add principals. Every durable write still names exactly one owner principal.

## Evidence versus ownership

Evidence can be visible to more than one authorized principal. Ownership belongs to the derived record, not automatically to its source.

Example: one conversation can support both a user preference and an agent lesson. Store two derivations with a shared source reference. Do not create a single hybrid record.

## Provenance minimum

Every generated durable claim records:

- source evidence references;
- source principal/actor when known;
- derived owner principal;
- derivation type;
- derivation run/version;
- claim state;
- confidence where applicable.

Repeated transformations of the same source do not count as independent evidence.

## User Dreaming

User Dreaming is allowed to derive only user-owned memory. It may:

- connect evidence across time;
- summarize repeated preferences/interests;
- record contradictions instead of forcing resolution;
- update confidence when genuinely new independent evidence exists;
- produce candidates for user-context projections.

It may not:

- mutate agent identity/persona;
- activate agent behavioral shifts;
- treat agent-authored interpretation as user-authored evidence;
- increase confidence merely because an earlier dream output repeats the claim.

## Agent autobiographical growth

The agent autobiographical subsystem derives only agent-owned identity/history. It may cite interactions with the user, but must distinguish what the user actually said/did from the agent's interpretation or lesson.

It may not create or rewrite user-owned beliefs as a side effect of self-reflection.

## Retrieval

Every memory query executes as an acting principal. Cross-principal reads require an explicit Chronicle ACL/topology rule. Read authorization never grants ownership or mutation authority.

## Epistemic correction/retraction

Use when a proposition should no longer be treated as true/useful.

For a user-owned claim:

1. mark/retract the user claim according to Chronicle semantics;
2. invalidate dependent user-derived memories/projections;
3. preserve correction provenance;
4. re-run affected user synthesis where useful;
5. do not rewrite unrelated agent autobiography.

For an agent-owned claim, perform the analogous operation only in agent-owned identity/self-model state.

## Privacy erasure

Privacy erasure removes or redacts the personal content itself, not merely belief in it. It can cross derived-principal boundaries because agent autobiography may reproduce user-sensitive content.

A privacy-erasure operation must trace provenance/dependents and remove or redact reproductions in:

- user durable memory;
- user projections;
- generated derived artifacts under system control;
- agent autobiographical records that reproduce the erased personal value;
- indexes/caches that cannot safely retain the value.

Non-sensitive structural tombstones may remain when required to prevent re-ingestion, but must not reproduce the erased content.

## Projection rules

USER.md/Daily Context and directive context are rebuildable projections. They do not become canonical merely because they are injected every session. Retraction/erasure must trigger projection rebuild when affected.

## Invariants

- no ownerless durable personal memory;
- no implicit global personal-memory namespace;
- no user-memory write from agent autobiography;
- no agent-identity write from User Dreaming;
- no confidence gain from circular self-citation;
- no cross-principal mutation implied by cross-principal read access;
- correction and privacy erasure are distinct operations.
