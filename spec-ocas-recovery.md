# spec-ocas-recovery.md — Recovery, Self-Diagnosis, and Self-Repair

Spec Version: 0.1.0 (draft)
Author: Indigo Karasu

---

## Purpose

This document defines the standard recovery, self-diagnosis, and self-repair contracts for OCAS skills. Every skill that runs on a schedule, produces side effects, or maintains durable state MUST implement these patterns.

The goal: no work is ever silently lost, no failure is ever invisible, and no recurring problem persists without the system either fixing itself or escalating with a diagnosis.

---

## 1. Three-Layer Recovery Model

### Layer 1 — Durable Intent Queue (DIQ)

Every action with side effects is recorded as an intent *before* execution. If the execution fails, the next wake picks it up.

#### Intent schema (`intents.jsonl`, append-only):

```json
{
  "intent_id": "unique-slug",
  "created": "ISO-8601",
  "status": "staged",
  "action_type": "<verb>",
  "condition_snapshot": { "<trigger fields>" },
  "expected_outcomes": [ "<what should change>" ],
  "max_attempts": 10,
  "stale_threshold_hours": 72,
  "attempts": 0,
  "last_error": null,
  "superseded_by": null
}
```

#### State machine:

```
staged → in_progress → complete
staged → superseded   (condition no longer holds)
staged → stale        (max_attempts AND stale_threshold_hours exceeded)
staged → cancelled    (manual)
```

#### Processing rules:

1. Every scheduled wake reads the DIQ before doing new work.
2. For each `staged` or `in_progress` intent, re-evaluate `condition_snapshot` against fresh data.
3. If condition no longer holds: mark `superseded`, log rationale.
4. If condition holds: attempt execution. On success → `complete`. On failure → increment `attempts`, keep `staged`, record `last_error`.
5. If `attempts >= max_attempts` AND age > `stale_threshold_hours`: mark `stale`, write summary to decisions log.
6. New plans for the same target supersede old `staged` intents for that target.

#### Storage:

```
{agent_root}/commons/data/{skill-name}/intents.jsonl
```

### Layer 2 — Execution Evidence Log (EEL)

Every run writes an evidence record, including runs where nothing happened. This is how you distinguish "nothing to do" from "something went wrong silently."

#### Evidence schema (`evidence.jsonl`, append-only):

```json
{
  "run_id": "<skill>_<timestamp>",
  "timestamp": "ISO-8601",
  "status": "ok | error | skipped",
  "gap_detected": null | "<description>",
  "intents_processed": 0,
  "intents_executed": 0,
  "intents_superseded": 0,
  "intents_stale": 0,
  "side_effects_executed": false,
  "side_effect_summary": "<what happened>",
  "not_activity_reason": null | "<why nothing happened>",
  "error": null | "<error class>"
}
```

#### The `not_activity_reason` field (mandatory for no-op runs):

When a run produces no side effects, this field MUST explain why. Examples:

- `"no_drift_triggers"` — Rally: portfolio within drift thresholds
- `"safety_gate_blocked: clause_4"` — Rally: drawdown exceeds max
- `"no_new_journals"` — Lucid: no unprocessed journals found
- `"token_failed_fallback_used"` — Dispatch: Gmail token broken, used cached data
- `"market_closed"` — Rally: broker clock reports holiday
- `"no_actionable_messages"` — Dispatch: inbox classified, nothing requires response
- `"all_within_thresholds"` — Bones: no markets with significant price movement

Without this field, a silent failure and a deliberate no-op are indistinguishable.

### Layer 3 — Self-Diagnosis & Self-Repair Loop (SDSR)

When the EEL produces something unexpected — gap detected, repeated errors, stale intents piling up — the skill enters a diagnostic routine.

#### 3a. Classify the failure:

| Category | Description | Example |
|---|---|---|
| `transient` | Self-resolving, retry is sufficient | API rate limit, network timeout, provider 502 |
| `persistent` | Requires intervention | Auth failure, config corruption, data source gone |
| `structural` | Bug in the skill itself | Script error, schema mismatch, logic bug |
| `degraded` | Data source unavailable, fallback active | Yahoo Finance down, using cached prices |

**Rule**: Transient errors self-resolve within 1-2 retries. Persistent errors need escalation. Structural errors need Forge. Degraded mode needs a flag in the evidence log.

#### 3b. Determine fixability:

| Fixability | Action |
|---|---|
| `self-fixable` | Skill repairs and logs the repair |
| `escalatable` | Skill writes a diagnostic report and notifies the user |
| `praxis` | Behavioral pattern issue — invoke Praxis to extract lesson |
| `forge` | Structural/tooling issue — invoke Forge to rebuild |

#### 3c. Self-repair protocol:

1. Collect evidence: error messages, retry counts, data freshness, dependency status.
2. Classify the failure (3a).
3. If self-fixable: execute repair → write `repair` decision entry → re-validate.
4. If not self-fixable: write `escalation` decision entry → notify user with diagnosis.
5. After re-validation: write result. If repair failed → escalate.

#### 3d. Re-validation requirement:

**No self-repair is logged as successful until re-validation passes.** Run a verification check after every repair. If re-validation fails, the repair is logged as `failed` and escalated.

---

## 2. Schedule Gap Detection

Every scheduled wake checks the evidence log for the most recent completed run. If the gap exceeds the expected cadence, a `gap_detected` entry is written and a remedial pass runs.

### Cadence thresholds:

| Skill type | Expected cadence | Gap threshold |
|---|---|---|
| Every N minutes | N minutes | 2x N |
| Daily | 24 hours | 1.5x (36h) |
| Weekly | 7 days | 1.5x (10.5h) |
| Multi-daily | Per schedule | 2x interval |

### Remedial action:

1. Write `gap_detected` to evidence log with gap description.
2. Run a compact remedial pass (subset of normal work, focused on what was missed).
3. Log what was recovered.
4. If gap > 2x threshold: escalate — the scheduler itself may be down.

### Gap recovery patterns:

- **Single missed run**: Process normally, catch up on missed work.
- **Multiple missed runs**: Run compact pass for each missed window, oldest first. Cap at 3 windows per wake to avoid overload.
- **Scheduler failure**: After recovery, verify cron jobs are still registered. Re-register any missing jobs.

---

## 3. Dependency Degradation

Skills that depend on external services (APIs, databases, other skills) MUST detect and handle degradation gracefully.

### Degraded mode contract:

1. When a dependency fails, the skill enters degraded mode.
2. Degraded mode MUST produce output (possibly reduced), not skip silently.
3. The evidence log records `degraded: <dependency>`.
4. On next wake, retry the dependency. If restored, exit degraded mode.
5. If a dependency is degraded for > `config.recovery.degraded_escalation_hours` (default 24), escalate.

### Fallback cascade pattern:

```
1. Primary source
   ↓ (fails)
2. Secondary source
   ↓ (fails)
3. Cached data
   ↓ (fails)
4. Skip with explanation + escalate if critical
```

Each fallback is logged in the evidence log: `fallback_used: <source> → <source>`.

---

## 4. Data Integrity Checks

Skills that maintain durable state MUST validate data integrity before writes and detect corruption after the fact.

### Pre-write validation:

Before writing state that other skills depend on:
1. Validate required fields are present and correctly typed.
2. Check referential integrity (foreign keys exist).
3. Verify data is within reasonable ranges (no 10x outliers from corrupted fields).
4. On validation failure: **abort the write**, log `validation_failed`, do not write partial/corrupted data.

### Post-corruption detection:

1. On read, if data fails schema validation: log `corruption_detected`.
2. Attempt recovery from backup or prior version.
3. If recovery possible: restore, log `auto_recovered`, re-validate.
4. If recovery impossible: log `corruption_unrecoverable`, escalate.

### Append-only file safety:

Files that are append-only (JSONL logs, evidence, intents) can still be corrupted by:
- Mid-write interruption (partial last line)
- Encoding errors (invalid UTF-8)
- Accidental overwrite (write_file instead of append)

**Recovery**: Truncate the last incomplete line. Verify file parses as valid JSONL. Log the truncation in decisions.

---

## 5. Idempotency

All self-repair and recovery operations MUST be idempotent. Running the same repair twice produces the same result as running it once.

### Idempotency mechanisms:

1. **Checkpoint files**: Before an operation, record the intent. After completion, mark it done. On restart: skip completed checkpoints.
2. **Deduplication keys**: Use `run_id`, `intent_id`, or external object IDs to prevent double-processing.
3. **Merge semantics**: State updates merge, never blindly overwrite.
4. **External side-effect guards**: Before calling an external API, check if the action was already performed (query first).

---

## 6. Escalation Format

When a skill cannot self-repair, it writes an escalation record:

```json
{
  "escalation_id": "<skill>_<timestamp>",
  "timestamp": "ISO-8601",
  "severity": "warning | error | critical",
  "category": "transient | persistent | structural | degraded",
  "summary": "<one-line description>",
  "diagnosis": "<detailed analysis>",
  "evidence": { "error_log_sample": "...", "retry_count": N, "gap_hours": N },
  "recommended_fix": "<what the user should do>",
  "auto_fix_attempted": true,
  "auto_fix_result": "failed: <reason>"
}
```

Escalation records are written to `decisions.jsonl` with `decision_type: "escalation"`.

---

## 7. OKR Integration

Every skill's OKRs (per `spec-ocas-journal.md`) MUST include at least these recovery-specific metrics:

| OKR | Metric | Target | Window |
|---|---|---|---|
| schedule_adherence | fraction of expected runs that produced evidence | ≥ 0.98 | 30 runs |
| recovery_success_rate | fraction of self-repairs that pass re-validation | ≥ 0.90 | 30 runs |
| mean_time_to_detect | average gap between failure and detection | ≤ 1 run | 30 runs |
| false_no_op_rate | fraction of no-op evidence records that were actually errors | ≤ 0.01 | 30 runs |
| data_integrity | fraction of reads that pass schema validation | 1.00 | 30 runs |

---

## 8. Skill Cooperation for Recovery

### Praxis (behavioral refinement):

When a failure pattern repeats ≥ 2 times across runs, the skill invokes Praxis:
1. Record the pattern as an event: `"recurring_failure: <category>, count: N"`.
2. Praxis extracts a micro-lesson and proposes a behavior shift.
3. On activation: the shift modifies how the skill approaches the problematic operation.

### Forge (structural repair):

When the skill identifies a structural issue (script bug, schema drift, config corruption):
1. Write a Forge intake request to `{agent_root}/commons/data/forge/intake/<issue>.json`.
2. Forge builds a fix (patch, rebuild, config restore).
3. The skill verifies the fix passes re-validation.

### Custodian (system health):

Custodian is the system-wide monitor. Individual skills handle their own failures. Custodian handles:
- Gateway/cron scheduler failures that affect multiple skills.
- Cross-skill dependency failures (e.g., MCP server down).
- Disk space, stale locks, zombie processes.

**Rule**: A skill should escalate to Custodian only for issues outside its own control.

---

## 9. Log Compaction (Self-Cleanup)

Skills MUST implement self-cleanup of recovery logs to prevent unbounded growth. The rule: **compact, never blind-delete. Preserve shape, reduce granularity.**

### Compaction thresholds:

| Log type | Compaction age | Method | Retain |
|---|---|---|---|
| `evidence.jsonl` (no-op entries) | 30 days | Daily summary | Last 7 days uncompacted |
| `evidence.jsonl` (error/gap entries) | 90 days | Weekly summary | Last 14 days uncompacted |
| `decisions.jsonl` (routine entries) | 90 days | Weekly summary | Last 14 days uncompacted |
| `decisions.jsonl` (escalation entries) | Never | — | Permanent until acknowledged |
| Ingestion/idempotency logs | 30 days | Range summary: `(skill, from, to, count, all_ok)` | Last 7 days uncompacted |
| `intents.jsonl` (terminal state) | 30 days | Merge: `(intent_id, created, completed, outcome)` | Last 7 days + all stale |

### Compaction format:

A compaction entry replaces N old entries:

```json
{
  "compaction": true,
  "original_count": 30,
  "date_from": "2026-04-01",
  "date_to": "2026-04-30",
  "summary": "30 runs, 0 errors, 0 gaps, 0 repairs, 2 escalations",
  "errors": [],
  "gaps": [],
  "escalations": ["esc_20260415_token_expires", "esc_20260422_disk_full"],
  "compacted_at": "2026-05-01T03:00:00Z"
}
```

### Compaction rules:

1. **Compaction is idempotent**: Track the compaction boundary (last compacted timestamp). Re-running compaction must not re-compact already-compacted ranges.
2. **Never compact the most recent 7 days**: Always keep at least the last week of raw entries for debugging.
3. **Escalations are permanent**: Never compact or delete escalation records. The user must explicitly acknowledge (mark `resolved`).
4. **Compaction writes an evidence entry**: After compaction, write an evidence entry with `not_activity_reason: "log_compaction"`, `side_effect_summary: "compacted N entries from date range"`.
5. **Atomic write**: Write compaction summary to a temp file, then rename. Never write partial compaction.
6. **Compaction failure**: If compaction fails mid-way (interrupted), the partial compaction file is detected on next run and discarded. Original entries are untouched.

### What NOT to delete:

- **The last entry in any log**: Always retains the current cursor position for gap detection.
- **The last entry before a gap**: Gap recovery needs the pre-gap timestamp.
- **Any entry referenced by an active escalation**: Check escalation records before compacting. If an escalation references evidence entries, keep those entries.

### Storage budget:

A well-compacted recovery system should not exceed:
- `evidence.jsonl`: ~50KB per skill (even after years of daily runs)
- `decisions.jsonl`: ~200KB per skill (retains escalations + summaries)
- `intents.jsonl`: ~10KB per skill (only active + recent terminal)

If a skill's recovery logs exceed these budgets by 2x, compaction is overdue and should be escalated.

---

## 10. Recovery Storage Layout

```
{agent_root}/commons/data/{skill-name}/
  intents.jsonl           — durable intent queue
  evidence.jsonl          — execution evidence log
  decisions.jsonl         — includes escalation and repair records
  recovery/
    checkpoints/          — process checkpoint files for resumable operations
    diagnostics/          — detailed diagnostic output for escalations
```

---

## 11. Implementation Checklist

For each OCAS skill, verify:

- [ ] **DIQ**: Side-effect actions are recorded as intents before execution
- [ ] **DIQ**: Intent state machine is implemented (staged → complete/superseded/stale)
- [ ] **DIQ**: Queue is swept every wake before new work
- [ ] **EEL**: Every run writes an evidence record
- [ ] **EEL**: No-op runs include `not_activity_reason`
- [ ] **Gap detection**: Schedule gaps are detected and logged
- [ ] **Gap recovery**: Remedial work runs after gaps
- [ ] **Degraded mode**: Dependency failures activate degraded mode, not silent skip
- [ ] **Fallback cascade**: Documented and logged
- [ ] **Pre-write validation**: State writes are validated before commit
- [ ] **Post-corruption detection**: Reads validate schema, corruption is logged
- [ ] **Idempotency**: Recovery operations are idempotent
- [ ] **Escalation format**: Escalation records follow the standard schema
- [ ] **OKR**: Recovery-specific OKRs are declared
- [ ] **Praxis hook**: Recurring failures trigger Praxis
- [ ] **Forge hook**: Structural issues trigger Forge
- [ ] **Compaction**: Old logs are compacted per thresholds (not blind-deleted)
- [ ] **Compaction idempotency**: Compaction boundary tracked, re-rates are safe
- [ ] **Escalation retention**: Escalation records never auto-deleted

---

## Appendix A: Patterns by Skill

| Skill | DIQ | EEL | Gap Detect | Degraded | Self-Repair |
|---|---|---|---|---|---|
| Rally | ✅ pending_actions | ✅ decisions | ✅ schedule | ✅ data sources | ✅ safety gate retry |
| Dispatch | ✅ drafts queue | ✅ decisions | ✅ triage age | ✅ token fallback | ✅ stub cleanup |
| Bones | — | ✅ decisions | — | — | ✅ postmortem fixes |
| Sands | — | ✅ decisions | — | ✅ token refresh | — |
| Spot | ✅ watch.jsonl | ✅ journal | — | ✅ VPN rotation | ✅ bot block recovery |
| Bower | ✅ proposals | ✅ scan_events | — | — | ✅ auto-approve precision |
| Elephas | ✅ signals queue | ✅ ingestion_log | ✅ consolidation gap | — | ✅ orphan resolution |
| Lucid | ✅ recirculation_queue | ✅ ingestion_log | ✅ hibernation | ✅ MemPalace | — |
| Praxis | ✅ signals_evaluated | ✅ journal | — | — | ✅ shift consolidation |
| Forge | — | ✅ journal | — | — | — |
| Custodian | — | ✅ journal | ✅ cron health | — | ✅ auto-fix registry |
| Weave | — | ✅ journal | ✅ sync age | ✅ lock recovery | ✅ checkpoint resume |

---

## Appendix B: Anti-Patterns

**Never do these:**

1. **Silent skip**: Detecting a problem and not logging it.
2. **Write-before-validate**: Writing state without pre-write validation.
3. **Infinite retry**: Retrying a persistent failure without escalation or circuit-breaking.
4. **Orphaned intent**: Creating an intent record but never processing it.
5. **Evidence-free run**: Completing a scheduled run without writing evidence.
6. **No-op opacity**: Producing no output without explaining why.
7. **Degraded silence**: Entering degraded mode without logging it.
8. **Non-idempotent repair**: A repair that produces different results on re-run.
9. **Cross-skill state writes**: Skill A writing to Skill B's data directory.
10. **Unbounded queue**: Intent queue growing without stale eviction.
11. **Blind deletion**: Deleting old logs without compaction. Destroys audit trails and breaks gap detection.
12. **Compaction without idempotency**: Re-compacting already-compacted ranges, causing data loss on re-runs.
