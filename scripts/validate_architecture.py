#!/usr/bin/env python3
"""Validate OCAS v2 architecture registry, principal boundaries, and retired dependencies."""

from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "components.json"

NORMATIVE = [
    ROOT / "spec-ocas-architecture.md",
    ROOT / "spec-ocas-principals-and-memory-boundaries.md",
    ROOT / "spec-ocas-user-dreaming.md",
    ROOT / "spec-ocas-runtime-contracts.md",
    ROOT / "spec-ocas-interfaces.md",
    ROOT / "spec-ocas-storage-conventions.md",
    ROOT / "spec-ocas-shared-schemas.md",
    ROOT / "spec-ocas-journal.md",
    ROOT / "spec-ocas-recovery.md",
    ROOT / "ocas-skill-authoring-rules.md",
    ROOT / "ocas-build-template.md",
]

ALLOWED_STATUS = {"active", "transitional", "planned", "support"}
HISTORICAL_HINTS = (
    "retired", "replaced", "legacy", "historical", "migration",
    "formerly", "previous", "must not", "no new contract",
)

FORBIDDEN_SURFACES = {
    r"commons/db/ocas-elephas": "retired memory database path",
    r"Elephas\.query": "retired memory query API",
    r"Only Elephas writes": "retired memory ownership invariant",
    r"Corvus\s*(?:→|->)": "retired pattern-hub interface",
    r"MemPalace MCP": "retired memory-provider dependency",
}


def historical(line: str) -> bool:
    low = line.lower()
    return any(h in low for h in HISTORICAL_HINTS)


def main() -> int:
    errors: list[str] = []

    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"OCAS architecture validation FAILED\n- cannot parse components.json: {exc}", file=sys.stderr)
        return 1

    components = data.get("components", [])
    ids: set[str] = set()
    for comp in components:
        cid = comp.get("id")
        if not cid:
            errors.append("component missing id")
            continue
        if cid in ids:
            errors.append(f"duplicate component id: {cid}")
        ids.add(cid)

        status = comp.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"{cid}: invalid status {status!r}")
        if not comp.get("type") or not comp.get("layer") or not comp.get("visibility"):
            errors.append(f"{cid}: missing type/layer/visibility")
        if status == "transitional" and not comp.get("migration_obligation"):
            errors.append(f"{cid}: transitional component missing migration_obligation")

    retired = data.get("retired_components", {})
    overlap = set(retired) & ids
    if overlap:
        errors.append(f"retired component ids also current: {sorted(overlap)}")

    aliases: set[str] = set()
    for rid in retired:
        aliases.add(rid.lower())
        aliases.add(rid.removeprefix("ocas-").lower())

    for path in NORMATIVE:
        if not path.exists():
            errors.append(f"missing normative architecture file: {path.name}")
            continue

        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()

        for n, line in enumerate(lines, 1):
            low = line.lower()
            for alias in aliases:
                if re.search(rf"(?<![a-z0-9_-]){re.escape(alias)}(?![a-z0-9_-])", low):
                    if not historical(line):
                        errors.append(f"{path.name}:{n}: active-looking reference to retired {alias}")

        for pattern, label in FORBIDDEN_SURFACES.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                n = text.count("\n", 0, match.start()) + 1
                line = lines[n - 1] if lines else ""
                if not historical(line):
                    errors.append(f"{path.name}:{n}: {label}")

    arch = (ROOT / "spec-ocas-architecture.md").read_text(encoding="utf-8")
    for phrase in (
        "Chronicle is the durable memory/context substrate",
        "user principal",
        "agent principal",
        "User Dreaming",
        "Agent autobiographical",
        "Evidence may be shared; derived identity may not be conflated.",
    ):
        if phrase not in arch:
            errors.append(f"spec-ocas-architecture.md missing invariant: {phrase}")

    interfaces = (ROOT / "spec-ocas-interfaces.md").read_text(encoding="utf-8")
    if "never an interface" not in interfaces or "private" not in interfaces:
        errors.append("interfaces spec missing private-state boundary")
    if "target_principal" not in interfaces:
        errors.append("interfaces spec missing target_principal")

    dreaming = (ROOT / "spec-ocas-user-dreaming.md").read_text(encoding="utf-8")
    if "never writes agent identity/autobiography" not in dreaming:
        errors.append("User Dreaming contract missing agent-identity write prohibition")

    if errors:
        print("OCAS architecture validation FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    active = sum(1 for c in components if c.get("status") == "active")
    transitional = sum(1 for c in components if c.get("status") == "transitional")
    planned = sum(1 for c in components if c.get("status") == "planned")
    print(
        f"OCAS architecture validation OK: "
        f"{active} active, {transitional} transitional, {planned} planned; "
        f"{len(NORMATIVE)} normative specs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
