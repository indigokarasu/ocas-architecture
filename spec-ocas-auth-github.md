# spec-ocas-auth-github.md

Version: 1.0.0
Author: Indigo Karasu

---

## Purpose

This spec defines how OCAS skills and scripts authenticate with GitHub. It supplements `spec-ocas-scripts.md` (which covers auth patterns in general) with GitHub-specific conventions: environment variables, token storage, `gh` CLI usage, and the self-update contract.

**Related specs:** `spec-ocas-scripts.md` (general auth discipline), `ocas-skill-authoring-rules.md` (self-update requirement for all skills).

---

## Auth mechanisms

OCAS skills interact with GitHub in two distinct contexts:

| Context | Mechanism | Who sets it up |
|---|---|---|
| `scripts/` that call the GitHub REST/GraphQL API | `GITHUB_TOKEN` env var | Operator, via `~/.hermes/.env` |
| `self_update` blocks in SKILL.md and `skill.json` | `gh` CLI (authenticated separately) | Operator, via `gh auth login` or `GITHUB_TOKEN` |
| Agent runtime (Claude Code on the Web) | `claude auth github` OAuth flow | Operator, once per session or environment |

All three mechanisms are additive: a skill may rely on all of them. None is a substitute for the others.

---

## Environment variable

The canonical env var for GitHub API access in OCAS scripts is `GITHUB_TOKEN`.

- Set it in `~/.hermes/.env`.
- Scripts read it via `os.environ.get("GITHUB_TOKEN", "")`.
- A missing `GITHUB_TOKEN` is a fatal startup error: print one line to stderr naming the variable and the file, then exit `1`.
- Never fall through to `gh auth token` or another credential source silently — the operator cannot debug what they cannot see.

```python
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

def main():
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN not set. Add to ~/.hermes/.env.", file=sys.stderr)
        sys.exit(1)
```

Token scope requirements must be documented in the script's docstring under `Auth:`:

```
Auth: GITHUB_TOKEN in ~/.hermes/.env. Required scopes: repo (read), read:org.
```

---

## Token storage

For skills that need to store a refreshable OAuth token (e.g., a GitHub App installation token or a user OAuth token with a refresh cycle), the standard path is:

```
~/.hermes/github_token.json
```

Schema:

```json
{
  "access_token": "gho_...",
  "token_type": "bearer",
  "scope": "repo read:org",
  "expires_at": "2026-06-01T00:00:00Z"  // omit if non-expiring
}
```

Rules:

- The token file is never committed to any repository.
- Scripts that write a refreshed token write only to this path, not to any path inside the skill package.
- If `expires_at` is present and the token is expired or within 5 minutes of expiry, the script must attempt a refresh before proceeding. A refresh failure is a fatal error.
- If the token file is absent or malformed, exit `1` with a clear stderr message instructing the operator to run `gh auth login` or re-set `GITHUB_TOKEN`.

---

## `gh` CLI usage

All skills use the `gh` CLI for their `self_update` procedure. This is an OCAS-wide convention (see `ocas-skill-authoring-rules.md`).

**Prerequisite:** The operator must have run `gh auth login` (or exported `GITHUB_TOKEN`) in the environment where the agent runs. Skills must not attempt to authenticate `gh` on behalf of the operator.

Standard `self_update` shape:

```json
{
  "self_update": {
    "source": "github",
    "repo": "indigokarasu/<skill-repo>",
    "mechanism": "gh release download",
    "command": "gh release download --repo indigokarasu/<skill-repo> --pattern '*.zip' --dir /tmp && unzip -o /tmp/<skill>.zip -d {agent_root}/skills/",
    "requires_binaries": ["gh", "unzip"]
  }
}
```

If `gh` is not authenticated, the update command will fail with a `gh` error message. The skill must not wrap or suppress this error — let the operator see the raw `gh` output.

---

## Claude Code runtime auth

When OCAS skills are developed or operated within a **Claude Code on the Web** session, the agent runtime authenticates with GitHub via:

```
claude auth github
```

This initiates a GitHub OAuth web flow that grants the Claude Code session read/write access to repositories the operator authorizes. It is separate from `GITHUB_TOKEN` and from `gh auth login`.

When to run it:

- At the start of any Claude Code on the Web session that involves pushing commits, creating PRs, or reading private repositories via the agent runtime.
- It does not need to be re-run within a single session once authenticated.
- It does not replace `GITHUB_TOKEN` for scripts that call the GitHub API directly.

Skills must not assume `claude auth github` has been run. If a skill delegates a GitHub action to the agent runtime (rather than calling the API directly from a script), the action may fail silently in unauthenticated sessions. Document any such dependency in SKILL.md under `## Initialization`.

---

## Security checklist

- [ ] `GITHUB_TOKEN` read from `os.environ`, never hardcoded
- [ ] Token scope documented in script docstring
- [ ] `~/.hermes/github_token.json` (if used) excluded from all `.gitignore`-tracked paths
- [ ] No token value appears in logs, journal files, or stdout
- [ ] `self_update` block uses `gh release download`, not a hardcoded URL with embedded credentials
- [ ] Script exits `1` with actionable stderr if token is absent or expired

---

## Anti-patterns

- **Hardcoded tokens**: `GITHUB_TOKEN = "ghp_abc123"` in source. Immediate disqualification.
- **Silent fallback**: trying `GITHUB_TOKEN`, then falling back to `gh auth token` on failure. The operator cannot tell which path ran.
- **Token in journal**: logging `{"token": "ghp_..."}` to the journal. Chronicle ingests journals; a token there is a credential leak.
- **Unauthenticated assumption**: a skill that calls `gh pr create` from a script without checking that `gh` is authenticated. Check with `gh auth status` before any `gh` write operation.
- **Storing tokens inside the skill package**: `scripts/token.json`, `assets/github_creds.json`. The skill package is read-only at runtime and may be installed in shared locations.
