#!/usr/bin/env python3
"""Audit active repository content for references to retired OCAS systems.

Two modes:

  # Scan already-checked-out repositories below a workspace.
  python3 scripts/audit_legacy_references.py --workspace ~/src

  # Clone every accessible repository for an owner using the authenticated
  # GitHub CLI, then scan the default branches.
  python3 scripts/audit_legacy_references.py --owner indigokarasu

Historical journals and explicitly archived retired state are intentionally
excluded. They are evidence and must not be rewritten merely to make this
audit quiet.

Exit 0: no active violations.
Exit 1: one or more active violations.
Exit 2: audit could not run.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Iterable

SCRIPT_NAME = Path(__file__).name

TEXT_EXTENSIONS = {
    ".md", ".txt", ".py", ".sh", ".bash", ".zsh", ".json", ".jsonl",
    ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env", ".js",
    ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".html", ".css", ".sql",
}

ALWAYS_EXCLUDE_DIRS = {
    ".git", ".hg", ".svn", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", "vendor", ".next", ".cache",
}

# Historical evidence/state is preserved, not "cleaned up".
HISTORICAL_PATH_PATTERNS = (
    re.compile(r"(^|/)archive(/|$)", re.I),
    re.compile(r"(^|/)\.archive(/|$)", re.I),
    re.compile(r"(^|/)commons/archive/retired(/|$)", re.I),
    re.compile(r"(^|/)commons/journals/(?:ocas-)?(?:elephas|corvus)(/|$)", re.I),
    re.compile(r"(^|/)commons/data/(?:ocas-)?(?:elephas|corvus)(/|$)", re.I),
    re.compile(r"(^|/)commons/db/(?:ocas-)?elephas(/|$)", re.I),
    re.compile(r"(^|/)skills/\.archive(/|$)", re.I),
)

HISTORICAL_FILES = {
    "CHANGELOG.md",
    "todo.md",
}

# ocas-architecture owns the retirement registry and has its own stricter
# normative validator. The registry itself necessarily names retired systems.
ARCHITECTURE_SPECIAL_FILES = {
    "components.json",
    "scripts/audit_legacy_references.py",
}

HISTORICAL_LINE_MARKERS = (
    "retired", "legacy", "historical", "archived", "archive", "replaced",
    "replacement", "migration", "migrated", "former", "formerly",
    "no longer", "decommissioned", "must not", "do not use", "quarantine",
)

CODEISH_SUFFIXES = {
    ".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".cjs", ".ts", ".tsx",
    ".jsx", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".conf", ".env", ".sql",
}


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        timeout=600,
    )


def load_retired_terms(architecture_root: Path) -> set[str]:
    registry = architecture_root / "components.json"
    if not registry.exists():
        raise FileNotFoundError(f"components.json not found under {architecture_root}")
    data = json.loads(registry.read_text(encoding="utf-8"))
    terms: set[str] = set()
    for component_id in data.get("retired_components", {}):
        low = component_id.lower()
        terms.add(low)
        if low.startswith("ocas-"):
            terms.add(low[5:])
    return terms


def is_historical_path(rel: str) -> bool:
    normalized = rel.replace("\\", "/")
    if Path(normalized).name in HISTORICAL_FILES:
        return True
    return any(p.search(normalized) for p in HISTORICAL_PATH_PATTERNS)


def is_text_candidate(path: Path) -> bool:
    if path.name == SCRIPT_NAME:
        return False
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    # Common extensionless operational files.
    return path.name in {"Dockerfile", "Makefile", "Procfile"}


def line_is_historical(line: str) -> bool:
    low = line.lower()
    return any(marker in low for marker in HISTORICAL_LINE_MARKERS)


def term_pattern(term: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![a-z0-9_-]){re.escape(term)}(?![a-z0-9_-])", re.I)


def iter_repositories(workspace: Path) -> Iterable[Path]:
    if (workspace / ".git").exists():
        yield workspace
        return
    for child in sorted(workspace.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            yield child


def scan_repo(repo: Path, retired_terms: set[str]) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    repo_name = repo.name
    patterns = {term: term_pattern(term) for term in retired_terms}

    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in ALWAYS_EXCLUDE_DIRS]
        root_path = Path(root)
        for filename in files:
            path = root_path / filename
            rel = path.relative_to(repo).as_posix()

            if is_historical_path(rel):
                continue
            if repo_name == "ocas-architecture" and rel in ARCHITECTURE_SPECIAL_FILES:
                continue

            # A legacy system name in an active filename/path is itself a
            # violation even if the file happens not to mention the term.
            low_rel = rel.lower()
            for term, pattern in patterns.items():
                if pattern.search(low_rel):
                    violations.append({
                        "repo": repo_name,
                        "path": rel,
                        "line": 0,
                        "term": term,
                        "kind": "active_path",
                        "text": rel,
                    })
                    break

            if not is_text_candidate(path):
                continue

            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            for line_no, line in enumerate(text.splitlines(), 1):
                for term, pattern in patterns.items():
                    if not pattern.search(line):
                        continue

                    # Prose may discuss a retired system explicitly as history.
                    # Executable/config content gets the same exception only
                    # when the line clearly marks the name as retired/legacy;
                    # this permits quarantine sets such as RETIRED_COMPONENT_DIRS.
                    if line_is_historical(line):
                        continue

                    violations.append({
                        "repo": repo_name,
                        "path": rel,
                        "line": line_no,
                        "term": term,
                        "kind": "active_reference",
                        "text": line.strip()[:240],
                    })

    return violations


def clone_owner(owner: str, dest: Path, include_archived: bool) -> list[Path]:
    if shutil.which("gh") is None:
        raise RuntimeError("GitHub CLI 'gh' is required for --owner mode")
    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        raise RuntimeError("gh is not authenticated; run 'gh auth login' first")

    fields = "nameWithOwner,isArchived"
    listed = run([
        "gh", "repo", "list", owner, "--limit", "500",
        "--json", fields,
    ])
    if listed.returncode != 0:
        raise RuntimeError(listed.stderr.strip() or "gh repo list failed")

    repos = json.loads(listed.stdout)
    paths: list[Path] = []
    for item in repos:
        if item.get("isArchived") and not include_archived:
            continue
        full = item["nameWithOwner"]
        name = full.split("/", 1)[1]
        target = dest / name
        cloned = run([
            "gh", "repo", "clone", full, str(target),
            "--", "--depth", "1", "--filter=blob:none",
        ])
        if cloned.returncode != 0:
            print(f"WARN: could not clone {full}: {cloned.stderr.strip()}", file=sys.stderr)
            continue
        paths.append(target)
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--workspace", type=Path, help="directory containing checked-out repos")
    mode.add_argument("--owner", help="GitHub owner to clone and audit using gh")
    parser.add_argument(
        "--architecture-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="ocas-architecture checkout containing components.json",
    )
    parser.add_argument("--include-archived-repos", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit machine-readable result")
    args = parser.parse_args()

    try:
        retired_terms = load_retired_terms(args.architecture_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    temp: tempfile.TemporaryDirectory[str] | None = None
    try:
        if args.owner:
            temp = tempfile.TemporaryDirectory(prefix="ocas-legacy-audit-")
            repo_paths = clone_owner(
                args.owner,
                Path(temp.name),
                include_archived=args.include_archived_repos,
            )
        else:
            workspace = args.workspace.expanduser().resolve()
            if not workspace.exists():
                print(f"ERROR: workspace does not exist: {workspace}", file=sys.stderr)
                return 2
            repo_paths = list(iter_repositories(workspace))

        violations: list[dict[str, object]] = []
        for repo in repo_paths:
            violations.extend(scan_repo(repo, retired_terms))

        result = {
            "repositories_scanned": len(repo_paths),
            "retired_terms": sorted(retired_terms),
            "violations": violations,
        }

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if violations:
                print(f"Legacy-system audit FAILED: {len(violations)} active reference(s)")
                for v in violations:
                    where = f"{v['repo']}/{v['path']}"
                    if v["line"]:
                        where += f":{v['line']}"
                    print(f"- {where}: {v['term']} ({v['kind']}) — {v['text']}")
            else:
                print(
                    f"Legacy-system audit OK: {len(repo_paths)} repositories; "
                    f"retired terms={', '.join(sorted(retired_terms))}"
                )

        return 1 if violations else 0
    except Exception as exc:
        print(f"ERROR: audit failed: {exc}", file=sys.stderr)
        return 2
    finally:
        if temp is not None:
            temp.cleanup()


if __name__ == "__main__":
    raise SystemExit(main())
