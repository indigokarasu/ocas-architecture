# spec-ocas-auth-claude.md

Version: 1.0.0
Author: Indigo Karasu

---

## Purpose

This spec defines how OCAS skills and scripts authenticate with the Anthropic Claude API. It supplements `spec-ocas-scripts.md` (general auth discipline) and `spec-ocas-auth-github.md` (GitHub auth) with Claude-specific conventions: the API key env var, model selection, the `claude auth login` runtime flow, and the journal provider field.

**Related specs:** `spec-ocas-scripts.md` (general auth discipline), `spec-ocas-journal.md` (model/provider fields in journal entries), `spec-ocas-auth-github.md` (GitHub auth patterns).

---

## Auth mechanisms

OCAS skills interact with the Claude API in two distinct contexts:

| Context | Mechanism | Who sets it up |
|---|---|---|
| `scripts/` that call the Anthropic API directly | `ANTHROPIC_API_KEY` env var | Operator, via `~/.hermes/.env` |
| Agent runtime (Claude Code on the Web) | `claude auth login` OAuth flow | Operator, once per session or environment |

The two mechanisms are independent. A script running outside the agent runtime needs `ANTHROPIC_API_KEY`; the agent runtime session uses its own credential established by `claude auth login`. Neither substitutes for the other.

---

## Environment variable

The canonical env var for Claude API access in OCAS scripts is `ANTHROPIC_API_KEY`.

- Set it in `~/.hermes/.env`.
- Scripts read it via `os.environ.get("ANTHROPIC_API_KEY", "")`.
- A missing `ANTHROPIC_API_KEY` is a fatal startup error: print one line to stderr naming the variable and the file, then exit `1`.
- Never fall through to another credential source silently.

```python
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def main():
    if not ANTHROPIC_API_KEY:
        print("Error: ANTHROPIC_API_KEY not set. Add to ~/.hermes/.env.", file=sys.stderr)
        sys.exit(1)
```

Document the key requirement in the script's docstring under `Auth:`:

```
Auth: ANTHROPIC_API_KEY in ~/.hermes/.env.
```

---

## Model selection

OCAS scripts that call the Claude API must not hardcode a model string in the call site. Instead:

- Resolve the model from a config field (e.g., `config.model`) or a dedicated env var (e.g., `OCAS_MODEL`).
- Fall back to a documented default defined as a module-level constant — not an inline string literal.
- The default must be a current, supported model identifier. Update it when the model is retired.

```python
DEFAULT_MODEL = "claude-sonnet-4-6"
MODEL = os.environ.get("OCAS_MODEL", DEFAULT_MODEL)
```

Document the default and the override in the script docstring.

Every journal entry emitted by a Claude-calling script must include the `model` and `provider` fields per `spec-ocas-journal.md`:

```json
{
  "model": "claude-sonnet-4-6",
  "provider": "anthropic"
}
```

This enables skill-to-model pairing analysis and helps Mentor evaluate whether a model change affected outcome quality.

---

## `claude auth login` runtime flow

When OCAS skills are developed or operated within a **Claude Code on the Web** session, the agent runtime authenticates with Anthropic via:

```
claude auth login
```

This initiates an Anthropic OAuth flow that authenticates the Claude Code session. It is separate from `ANTHROPIC_API_KEY` — the API key is for scripts; `claude auth login` is for the runtime session itself.

When to run it:

- At the start of any Claude Code on the Web session used for OCAS development or skill execution.
- It does not need to be re-run within a single session once authenticated.
- It does not replace `ANTHROPIC_API_KEY` for scripts that call the Anthropic API directly.

Skills must not assume `claude auth login` has been run. If a skill delegates a generation task to the agent runtime rather than calling the API from a script, document that dependency in SKILL.md under `## Initialization`:

```
## Initialization
Requires an active Claude Code session authenticated via `claude auth login`.
```

---

## Security checklist

- [ ] `ANTHROPIC_API_KEY` read from `os.environ`, never hardcoded
- [ ] Key requirement documented in script docstring under `Auth:`
- [ ] Model resolved from config or env var; default defined as a module-level constant
- [ ] Journal entries include `model` and `provider` fields
- [ ] No key value appears in logs, journal files, or stdout
- [ ] Script exits `1` with actionable stderr if key is absent

---

## Anti-patterns

- **Hardcoded API key**: `ANTHROPIC_API_KEY = "sk-ant-..."` in source. Immediate disqualification.
- **Hardcoded model string**: `model="claude-sonnet-4-6"` inline at every call site. Use a module-level constant so updates are a one-line change.
- **Key in journal**: logging `{"api_key": "sk-ant-..."}` to the journal. Chronicle ingests journals; a key there is a credential leak.
- **Silent fallback**: trying `ANTHROPIC_API_KEY`, then falling back to a different env var or config field on failure. The operator cannot tell which credential path ran.
- **Missing journal model field**: omitting `model` and `provider` from journal entries. Mentor cannot evaluate model impact on outcomes without this data.
- **Assuming runtime auth in scripts**: a script that calls `subprocess.run(["claude", ...])` and expects the runtime session's credentials to be available. Scripts are standalone processes; they need their own `ANTHROPIC_API_KEY`.
