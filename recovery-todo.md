# Recovery Standardization Tasks

Read `spec-ocas-recovery.md` from this repo first. Then work through the skills below. For each skill: read its SKILL.md, check which of the 4 recovery functions it already has, add only what's missing. Use `patch` tool with `mode=replace`. Don't change existing content.

## The 4 Functions (check each)

1. **Evidence Logging** — Does the skill write a record on every run, including no-op runs with a reason? If missing, add a Recovery Behavior section with evidence logging.
2. **Gap Detection** — Does the skill check for missed runs on wake? If missing and the skill has scheduled runs, add gap detection. Skip for on-demand-only skills.
3. **Degraded Mode** — Does the skill handle dependency failures with fallback? If missing and the skill has external dependencies, add degraded mode. Skip for skills with no external deps.
4. **Log Compaction** — Does the skill compact old logs instead of blind-deleting? If missing, add log compaction.

## Additional changes (all skills)

- Add `intents.jsonl` and `evidence.jsonl` to Storage Layout if not present
- Add `schedule_adherence` and `data_integrity` OKRs if not present
- Create empty `evidence.jsonl` and `intents.jsonl` files if they don't exist

## Skills

Skills marked **AUDIT** already have some recovery content — check for gaps only, don't duplicate.

| # | Skill | Scheduled? | Notes |
|---|---|---|---|
| 1 | ocas-bones | ✓ | |
| 2 | ocas-bower | ✓ | |
| 3 | ocas-corvus | ✓ | |
| 4 | ocas-custodian | ✓ | **AUDIT** — has auto-fix, escalation |
| 5 | ocas-dispatch | ✓ | **AUDIT** — has fallback cascade, stub cleanup |
| 6 | ocas-elephas | ✓ | **AUDIT** — has ingestion pipeline, orphan resolution |
| 7 | ocas-fellow | ✓ | |
| 8 | ocas-finch | ✓ | **AUDIT** — has scan/work pipeline |
| 9 | ocas-forge | ✓ | |
| 10 | ocas-haiku | ✓ | |
| 11 | ocas-imagine | | on-demand |
| 12 | ocas-inception | | on-demand |
| 13 | ocas-look | ✓ | |
| 14 | ocas-lucid | ✓ | |
| 15 | ocas-mentor | ✓ | |
| 16 | ocas-multipass | | on-demand, **AUDIT** — has checkpoint/resume |
| 17 | ocas-praxis | ✓ | |
| 18 | ocas-rally | ✓ | **AUDIT** — has pending-action queue, gap detection |
| 19 | ocas-reach | ✓ | |
| 20 | ocas-sands | ✓ | |
| 21 | ocas-scout | ✓ | |
| 22 | ocas-sift | ✓ | |
| 23 | ocas-spot | ✓ | **AUDIT** — has VPN rotation, bot block recovery |
| 24 | ocas-styx | | on-demand |
| 25 | ocas-taste | ✓ | |
| 26 | ocas-vesper | ✓ | **AUDIT** — has cooperative read patterns |
| 27 | ocas-vibes | | on-demand |
| 28 | ocas-voyage | ✓ | |
| 29 | ocas-weave | ✓ | |

## After completion

Write a summary to `recovery-update-summary.md` in this repo listing: per-skill which functions were present vs added, total count.
