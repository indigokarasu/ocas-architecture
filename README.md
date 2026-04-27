# OCAS Architecture

Private repository containing the system architecture specifications, shared schemas, and design documents for the OpenClaw Agent Suite (OCAS).

## Specifications

| File | Description | Version |
|---|---|---|
| `spec-ocas-architecture.md` | System overview, layers, data flow, invariants | 1.3 |
| `spec-ocas-interfaces.md` | Inter-skill intake contracts, cooperative queries, signal formats, handoff paths | 1.4.0 |
| `spec-ocas-journal.md` | Journal format, OKR evaluation, champion/challenger model | 1.2.3 |
| `spec-ocas-ontology.md` | Entity type hierarchy, skill extraction ownership, identity model | 2.2.0 |
| `spec-ocas-shared-schemas.md` | Canonical cross-cutting data schemas and domain extensions | 1.1.4 |
| `spec-ocas-storage-conventions.md` | Storage roots, naming conventions, retention rules | 1.0.3 |
| `spec-ocas-workflow-plans.md` | Workflow plan format, parameter system, expected bundled plans | 1.1.3 |
| `spec-ocas-skill-publishing.md` | README, CHANGELOG, and release structure standard | 1.0 |
| `spec-ocas-scripts.md` | `scripts/` directory best practices: CLI shape, auth, paths, boundary discipline | 1.0.0 |

## Build Documentation

| File | Description | Version |
|---|---|---|
| `ocas-build-template.md` | Canonical SKILL.md template for new skills | 2.2.0 |
| `ocas-skill-authoring-rules.md` | Rules and conventions for skill authorship | 2.8.0 |

## Active skill repositories (as of 2026-04-23)

| Skill | Repository | Version |
|---|---|---|
| ocas-forge | `indigokarasu/Forge` | 2.7.0 |
| ocas-relay | `indigokarasu/Relay` | 1.1.0 |
| ocas-rally | `indigokarasu/rally` | 3.5.4 |

All other OCAS skills (scout, sift, look, thread, corvus, weave, taste, voyage, sands, dispatch, vesper, custodian, spot, haiku, bower, elephas, mentor, praxis, fellow, multipass, vibes, triage) are currently historical reference: no instantiated GitHub repository exists under `indigokarasu`. See `spec-ocas-ontology.md` Skill Entity Extraction Ownership section for the complete historical list.

## Changes

See [CHANGELOG.md](CHANGELOG.md) for a summary of changes by date.

## Private

This repository is private. These specifications are internal design documents for the OCAS system. Do not publish or distribute.
