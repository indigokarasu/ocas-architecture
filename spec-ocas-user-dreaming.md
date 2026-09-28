# OCAS User Dreaming

Spec Version: 1.0.0
Author: Indigo Karasu
Status: normative contract

## Purpose

User Dreaming is offline consolidation that improves the agent's understanding of the user over time.

It is not the agent's own dream/autobiography system.

## Ownership

Every durable accepted result belongs to the user principal and preserves provenance to user-grounded evidence.

User Dreaming never writes agent identity/autobiography and never activates agent behavior shifts.

## Eligible inputs

- user-authored conversation spans;
- user-owned Chronicle claims/episodes;
- verified user-world events;
- explicit user corrections;
- relationship/preference signals with provenance;
- user-relevant journals that preserve source attribution.

## Ineligible as direct evidence of user truth

- assistant-authored statements;
- tool output without attribution;
- scheduler/host text;
- prior dream conclusions repeating the same source;
- recalled memory merely restating an existing belief;
- raw browsing activity without an approved derived-signal step.

## Pipeline

1. Select a bounded temporal/evidence window.
2. Resolve source ownership and speaker attribution.
3. Gather relevant user-principal claims, episodes, and eligible candidates.
4. Build temporal/entity links.
5. Generate candidate observations/inferences.
6. Separate observed, user-stated, inferred, predicted, disputed, and unknown states.
7. Verify each candidate against provenance.
8. Reject circular reinforcement and duplicate evidence.
9. Record contradictions without forcing synthesis.
10. Write accepted user-owned derived claims through Chronicle.
11. Verify durable writes.
12. Emit run evidence/dependency links.
13. Refresh bounded user projections only after durable state is verified.

## Candidate classes

- stable preference;
- temporal relationship;
- recurring context;
- relationship pattern;
- unresolved question;
- contradiction;
- interest;
- project/goal context;
- projection hint.

## Anti-feedback-loop rules

- a derived claim is not independent evidence for itself;
- multiple summaries of one source count as one lineage;
- rerunning without new evidence does not increase confidence merely through repetition;
- user-direct evidence outranks agent inference about the user;
- agent-authored interpretation remains inference;
- a projection cannot be re-ingested as fresh support for the belief that produced it;
- explicit user correction supersedes prior dream-derived conclusions unless genuinely new independent evidence creates a conflict.

## Temporal reasoning

Distinguish:

- event time;
- observation time;
- valid-from;
- valid-until;
- recurrence;
- stale/expired state.

Recorded does not mean currently true.

## Contradictions

When evidence conflicts:

- preserve both lineages;
- create a contradiction/dispute record;
- prefer explicit user correction when applicable;
- otherwise defer or apply Chronicle's configured contradiction policy;
- never silently overwrite provenance.

## Retraction repair

When an upstream user claim is corrected/retracted:

1. locate dream-derived dependents;
2. invalidate affected descendants;
3. re-run affected derivations when useful;
4. rebuild affected projections;
5. preserve correction/retraction provenance.

## Privacy erasure

Privacy erasure is broader than epistemic correction.

It traces downstream reproductions and may require redaction/tombstoning in user memory, user projections, generated artifacts, and agent autobiography that reproduced the sensitive value.

Ownership remains separate even when erasure crosses both domains.

## Scheduling and run identity

Each run records:

- run_id;
- principal;
- evidence window/watermarks;
- input fingerprint;
- derivation version;
- accepted/rejected counts;
- contradiction count;
- write verification result.

## Separation from agent dreams

User Dreaming:
- subject: user;
- output: user-owned derived memory.

Agent autobiographical dreaming:
- subject: agent;
- output: agent-owned autobiography/self-model.

Implementations and command names should make the subject explicit enough to prevent operator confusion.

## Success criteria

A successful run:

- writes only the user principal;
- never upgrades agent/tool/system text into user-direct evidence;
- never counts its own prior output as new evidence;
- preserves provenance;
- verifies durable writes;
- leaves unresolved contradictions unresolved;
- emits evidence even when no new memory is accepted.
