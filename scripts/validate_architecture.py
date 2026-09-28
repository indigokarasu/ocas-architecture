#!/usr/bin/env python3
"""Fail CI when active OCAS architecture reintroduces retired components or invalid registry state."""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "components.json"
SCAN = [
    ROOT / "spec-ocas-architecture.md",
    ROOT / "spec-ocas-interfaces.md",
    ROOT / "spec-ocas-storage-conventions.md",
    ROOT / "spec-ocas-shared-schemas.md",
    ROOT / "ocas-skill-authoring-rules.md",
    ROOT / "ocas-build-template.md",
]
ALLOW_HISTORICAL = {ROOT / "CHANGELOG.md", ROOT / "todo.md"}


def main() -> int:
    errors: list[str] = []
    data = json.loads(REGISTRY.read_text())
    ids = [c["id"] for c in data["components"]]
    if len(ids) != len(set(ids)):
        errors.append("components.json contains duplicate component ids")
    retired = set(data.get("retired_components", {}))
    active = {c["id"] for c in data["components"] if c.get("status", "").startswith("active")}
    overlap = retired & active
    if overlap:
        errors.append(f"retired components marked active: {sorted(overlap)}")

    forbidden = {
        "ocas-elephas": re.compile(r"\b(?:ocas-)?elephas\b", re.I),
        "ocas-corvus": re.compile(r"\b(?:ocas-)?corvus\b", re.I),
        "mempalace": re.compile(r"\bmempalace\b", re.I),
    }
    for path in SCAN:
        if not path.exists():
            errors.append(f"missing architecture file: {path.name}")
            continue
        text = path.read_text()
        for name, pattern in forbidden.items():
            if pattern.search(text):
                errors.append(f"{path.name}: active contract references retired {name}")

    # Memory contracts must explicitly name principal ownership.
    arch = (ROOT / "spec-ocas-architecture.md").read_text()
    for phrase in ("user principal", "agent principal", "User Dreaming", "Agent autobiographical"):
        if phrase not in arch:
            errors.append(f"spec-ocas-architecture.md missing invariant: {phrase}")

    if errors:
        print("OCAS architecture validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"OCAS architecture validation OK: {len(active)} active registry entries")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
