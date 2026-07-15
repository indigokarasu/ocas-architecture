# spec-ocas-scripts.md

Version: 1.1.0
Author: Indigo Karasu

---

## Purpose

This spec defines best practices for the `scripts/` directory inside an OCAS skill package. It is the operational complement to `ocas-skill-authoring-rules.md` (which only names `scripts/` without prescribing what goes in it) and to `ocas-build-template.md` (which gates *whether* a script is justified but not *how* to write one).

The aim is consistency: any agent reading `scripts/<x>.py` from any OCAS skill should know how to invoke it, where its data goes, and what it returns, without reading source.

**Related specs:** `ocas-skill-authoring-rules.md` (justification for `scripts/` at all), `spec-ocas-storage-conventions.md` (where script outputs land), `spec-ocas-journal.md` (every script run that performs work emits a journal).

---

## When a script earns its place

Scripts/ exists for **deterministic help that materially improves correctness or reliability**. Add a script only when at least one of these is true:

- The work involves an external API or data store that benefits from typed wrapping
- The work is multi-step and the steps must execute in a specific order
- The work has parameters that are easy to get wrong if reconstructed from prose
- The work runs from a cron job or heartbeat and must not depend on conversational context
- A failure mode is costly enough to justify a tested, versioned shape

Do **not** add a script when:

- The behavior is one or two model-native tool calls in sequence
- The script is a thin wrapper around a single curl-equivalent that has no real logic
- The script exists "just in case" — speculative scaffolding
- The script duplicates work an existing OCAS skill already owns (see Boundary Discipline below)

If a directory accumulates scripts that fail this gate, prune at the next minor release. Three lines of inline code beat a half-used helper.

---

## Directory & file naming

```
scripts/
  <action_or_source>.py        — primary connector or workflow
  <action_or_source>_<role>.py — variant only when role differs materially
```

Rules:

- Use **snake_case** filenames matching the source or action (`google_sync.py`, `katzilla.py`, `enrichment_control.py`)
- No version suffixes in filenames (`_v2.py`, `_v3.py`). Versioning lives in `CHANGELOG.md` and the SKILL.md frontmatter, not in script names. Old variants are deleted, not renamed.
- No language suffix in name unless the directory mixes languages (`script.sh` and `script.py` may coexist)
- No author/date prefixes (`indigo_2026_04_*.py`)
- One responsibility per file. If a file grows past ~600 lines, decompose by action, not by author preference.

---

## Required CLI shape

Every script under `scripts/` follows this contract unless its purpose makes it impossible (e.g., a pure library imported by another script):

1. **Module docstring** at the top giving usage and a worked example. The docstring is what `--help` (or no-arg invocation) prints.
2. **Subcommand-style argv**: `script.py <action> [json_params]` where `action` is a verb or noun-action, and `json_params` is a single JSON-encoded argument string. This matches the shape used by Reach (`katzilla.py query <agent> <action> '<params>'`) and works cleanly with `subprocess.run` from the agent runtime.
3. **JSON to stdout** for the success path. Pretty-printed (`indent=2`) is acceptable; one-line is acceptable. Mixed prose + JSON is not.
4. **Errors to stderr**, JSON envelope when programmatic, free text when fatal.
5. **Exit codes**: `0` success, `1` invalid usage / missing auth / unrecoverable error, `2` partial success with errors logged. Never exit `0` on a failure path.

Example skeleton:

```python
#!/usr/bin/env python3
"""
<source> connector — <one-line purpose>.

Usage:
  python3 <source>.py <action> [json_params]

Examples:
  python3 <source>.py list
  python3 <source>.py fetch '{"id": "abc"}'

Auth: <ENV_VAR> in ~/.hermes/.env.
"""
import json, os, sys

ENV_VAR = os.environ.get("ENV_VAR", "")

def fetch(params):
    ...

def main():
    if not ENV_VAR:
        print("Error: ENV_VAR not set. Add to ~/.hermes/.env.", file=sys.stderr)
        sys.exit(1)
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(0)
    action = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    handlers = {"list": list_, "fetch": fetch}
    if action not in handlers:
        print(f"Unknown action: {action}", file=sys.stderr); sys.exit(1)
    print(json.dumps(handlers[action](params), indent=2))

if __name__ == "__main__":
    main()
```

---

## Configuration — behavioral vs. secrets

OCAS skills read two distinct kinds of configuration, and they use **different mechanisms**. Conflating them is a submission-blocking defect (the Hermes `env-var-for-config` policy auto-closes PRs that violate it).

**Secrets / credentials** (API keys, OAuth tokens, passwords):
- MAY be read from environment variables.
- Standard location: `~/.hermes/.env` (loaded by the runtime; scripts read `os.environ`).
- Declared in SKILL.md frontmatter via `required_environment_variables`.
- A missing required secret is a fatal startup error (see Authentication & secrets above).

**Behavioral settings** (retention thresholds, feature flags, display prefs, paths, dry-run toggles, rate limits):
- MUST NOT be read from environment variables. `GENIE_*`, `<NAME>_MAX_AGE_DAYS`, `<NAME>_PATH`, `<NAME>_ENABLED`, etc. are all forbidden as user-facing controls.
- MUST be declared in SKILL.md frontmatter under `metadata.hermes.config` with a logical key (e.g. `genie.snapshot_max_age_days`). The storage key becomes `skills.config.<key>`.
- MUST be read at runtime from `$HERMES_HOME/config.yaml` under `skills.config.<key>`, falling back to the declared default when unset. Use PyYAML (Hermes already ships it). The shipped `telephony.py` optional-skill is the reference implementation.
- MUST be documented in the SKILL.md Configuration section as `skills.config.<key>` — never as an env-var name.
- MAY be overridden by a CLI flag (e.g. `--dry-run`), which takes precedence over `config.yaml`.

**Runtime-locating variables** (`HERMES_HOME`, `HERMES_PROFILE`) are the only environment inputs permitted for non-secret purposes; they identify where the skill runs, not how it behaves.

Correct pattern:
```python
def _skill_config(key, default):
    """Resolve skills.config.<key> from config.yaml, fall back to default."""
    import yaml
    path = os.path.join(os.environ.get("HERMES_HOME", "~/.hermes"), "config.yaml")
    try:
        with open(os.path.expanduser(path)) as fh:
            node = yaml.safe_load(fh) or {}
    except OSError:
        return default
    for part in ("skills", "config", "<skill>", key):
        node = node.get(part) if isinstance(node, dict) else None
        if node is None:
            return default
    return node

threshold = _skill_config("snapshot_max_age_days", 7)   # NOT os.environ.get("GENIE_SNAPSHOT_MAX_AGE_DAYS", 7)
```

Anti-pattern (rejects submission):
```python
threshold = int(os.environ.get("GENIE_SNAPSHOT_MAX_AGE_DAYS", 7))   # WRONG
```

---

## Authentication & secrets

- **Never commit credentials** — not API keys, not OAuth tokens, not session cookies, not hardcoded paths to private credential files.
- All auth values come from environment variables. Standard location: `~/.hermes/.env` (loaded by the runtime; scripts read from `os.environ`).
- A missing required env var is a fatal startup error: print one line to stderr identifying the var and the file to set it in, then exit `1`. **Do not fall through to a different auth source silently** — the next operator will lose hours debugging.
- For OAuth tokens stored at `~/.hermes/<name>_token.json`, the path itself is fine to reference, but the script must verify the token is valid (or refreshable) before proceeding.
- If a script needs to write secrets (e.g., a refreshed access token), it writes only to the standard location, never to a path inside the skill package.

---

## Path & storage discipline

Scripts respect `spec-ocas-storage-conventions.md`:

- **Read** from the skill package itself (`scripts/`, `references/`, `assets/`) — the package is read-only at runtime.
- **Write** only to:
  - `{agent_root}/commons/data/<skill-name>/` — config, JSONL logs, ephemeral state
  - `{agent_root}/commons/journals/<skill-name>/` — journal files
  - `{agent_root}/commons/db/<skill-name>/` — LadybugDB files (DB-backed skills only)
- Resolve `agent_root` once at module load: `Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))`. Never hardcode `/root/.hermes/` — it breaks on machines that aren't the production host.
- Never use `__file__`-relative paths to write data. The skill package may be installed read-only or in a path that varies between runtimes.

---

## Dependencies

- **Prefer the standard library.** `urllib.request` over `requests`, `json` over `pydantic`, `csv` over `pandas`, etc.
- If a non-stdlib dependency is required, document it in the script's docstring and in the skill's `README.md` under `## Dependencies → External`.
- Do not assume third-party packages are installed in the runtime. If they might be missing, attempt the import and exit with an actionable error.
- Compiled artifacts (`__pycache__/`, `*.pyc`, `*.so`) must not be tracked in git. Ensure `.gitignore` covers them at the repo root.

---

## Error envelopes & logging

For machine-readable failures (e.g., HTTP 4xx from an upstream API), return a JSON object on stdout with at minimum:

```json
{
  "error": "<short_code>",
  "message": "<human readable>",
  "details": { ... }            // optional, source-specific
}
```

For human-readable fatal errors (missing auth, unsupported action, bad params), write a single descriptive line to stderr and exit non-zero. Do not print stack traces unless `DEBUG=1` is set in the environment — agents log stderr verbatim and stack traces flood context.

For a long-running script:
- Use a dedicated log file under `{agent_root}/commons/data/<skill-name>/<script>.log`, written line-buffered.
- Keep stdout clean for the final result; agents that read stdout should not have to filter chatter.

---

## Idempotency

A re-run with the same arguments should produce a result consistent with the first run, or a no-op. Specifically:

- Writes to JSONL append-only logs are inherently idempotent if the script keys on a deduplication field (e.g., `run_id` or external object ID). Always include such a field.
- Writes to `config.json` or other state files should merge, not overwrite blindly.
- External side effects (POST/PATCH/DELETE) require a checkpoint file or an external query to verify the action hasn't already been performed. The convention is `{agent_root}/commons/data/<skill-name>/<script>_ckpt.txt`, one identifier per line.

If interrupted and rerun, the script must resume from the checkpoint, not restart from zero.

---

## Boundary discipline

Scripts must not duplicate the responsibilities of other OCAS skills. Each connector should be a thin shell over the underlying API; **synthesis, classification, and pattern detection happen elsewhere**.

Specifically:

- **No scoring or ranking inside a connector**. If a Reach source returns a list, it returns the list. Ranking belongs to the calling skill or the agent.
- **No interpretation of natural-language input**. Scripts take structured arguments. The agent translates user prose into those arguments.
- **No knowledge-graph writes** from a connector script. Chronicle writes flow through Elephas's ingestion path.
- **No journaling on behalf of another skill**. Each skill writes only to its own journal directory.
- **No cross-skill imports**. Skills communicate via journals and intake directories defined in `spec-ocas-interfaces.md`, not via Python imports across `~/.hermes/skills/<other-skill>/scripts/`.

If a script seems to need another skill's logic, the right move is one of: (a) use the other skill's journal output via the documented interface, (b) extract the shared logic into a small library that both skills depend on (rare; needs design review), or (c) recognize that the work belongs to the other skill and delegate.

---

## Executable bit & shebang

- Scripts intended to be run directly (`python3 scripts/x.py`) need:
  - `#!/usr/bin/env python3` as the first line
  - Executable mode (`chmod +x scripts/x.py` and a tracked `100755` mode in git)
- Scripts imported as libraries by other scripts may omit both.
- Shell scripts use `#!/usr/bin/env bash` and `set -euo pipefail`.

---

## Testing & verification

Each script must pass three checks before merge:

1. **Parse check**: `python3 -c "import ast; ast.parse(open('scripts/x.py').read())"` returns 0
2. **No-arg help**: `python3 scripts/x.py` prints the docstring and exits 0
3. **Auth-missing path**: with the relevant env var unset, the script exits non-zero with a clear stderr message identifying the variable

Where the script supports a mock or dry-run mode, document it in the docstring and add it as a fourth check.

Integration smoke tests (one real call per source) belong in `references/<source>_smoke.md` as a checklist, not in the repo.

---

## SKILL.md ↔ scripts contract

- Every script in `scripts/` is referenced from SKILL.md, either in the **Sources / Commands** section (if user-invocable) or in the **Execution loop / Background tasks** section (if invoked by the runtime).
- A script not referenced from SKILL.md is dead weight — remove it.
- Conversely, every command surface declared in SKILL.md must have a backing script (or be implemented by the skill loader). No promises without implementation.
- If SKILL.md describes parameters, they must match the script's argv parsing exactly. Mismatch is a bug.

---

## Anti-patterns

- **Stale variants**: `pipeline.py`, `pipeline_v2.py`, `pipeline_v3.py` all in the same directory. Pick one. Delete the others. (Versions live in git history and CHANGELOG.md.)
- **Hardcoded host paths**: `/root/.hermes/...` baked into source. Use the env-var resolution pattern.
- **Swallowed exceptions**: `try: ... except Exception: pass`. The agent has no way to know the work didn't happen.
- **Silent fallbacks**: trying credentials A, then silently switching to credentials B on failure. The operator will not know which credential set is actually in use.
- **Scripts that return text-only "summaries"**: an agent cannot reliably parse prose. Return JSON.
- **In-package state**: `scripts/state.json`, `scripts/cache/`, etc. State lives under `{agent_root}/commons/data/<skill>/`.
- **Tracked compiled artifacts**: `__pycache__/`, `*.pyc`, build outputs. Add `.gitignore` and `git rm -r --cached`.
- **Behavioral config in env vars**: `GENIE_SNAPSHOT_MAX_AGE_DAYS`, `<NAME>_PATH`, `<NAME>_ENABLED`, etc. These must come from `config.yaml` (`skills.config.<key>`), not `os.environ`. Secrets are the only thing that belongs in env/`.env`.
- **Cross-skill Python imports**: `from ocas_other_skill.scripts.x import y`. Use the documented interface.
- **Script that does the SKILL's job**: a single bloated script that drives the entire skill workflow end-to-end. Skills are routed by the agent; scripts are tools. If a script encodes the routing, the routing belongs in SKILL.md.

---

## Audit checklist

When reviewing a skill's `scripts/` directory:

- [ ] Each script's filename describes its action or source clearly
- [ ] No `_v2`/`_v3`/dated suffixes
- [ ] All auth via env vars; no committed secrets (`grep -rE "(api[_-]?key|token|secret).*=\s*['\"][a-zA-Z0-9_-]{20,}" scripts/`)
- [ ] All scripts parse (`python3 -c "import ast; ..."`)
- [ ] No `__pycache__/` or `*.pyc` tracked in git
- [ ] No hardcoded `/root/`, `/home/<user>/` paths — `agent_root` resolved from env
- [ ] Stdout is JSON or empty; chatter goes to a log file or stderr
- [ ] Each script is referenced from SKILL.md
- [ ] No script duplicates another OCAS skill's owned responsibility
- [ ] Each script's docstring includes Usage, one Example, and the auth env-var name
- [ ] Idempotency: repeated runs don't double-write or corrupt state
- [ ] Errors return non-zero exit codes; no silent failures
- [ ] **Behavioral config** (thresholds, paths, flags) read from `config.yaml` `skills.config.<key>`, NOT env vars — no `GENIE_*`/`<NAME>_*` env reads in `scripts/`
- [ ] Every behavioral setting declared in `metadata.hermes.config`; SKILL.md documents `skills.config.<key>` (not env-var names)

A skill failing two or more boxes is not ready. A skill failing on auth or boundary discipline must not ship.
