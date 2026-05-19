# OCAS Architecture

Private repository containing the system architecture specifications, shared schemas, and design documents for the OpenClaw Agent Suite (OCAS).

## Specifications

| File | Description | Version |
|---|---|---|
| `spec-ocas-architecture.md` | System overview, layers, data flow, invariants | 1.4 |
| `spec-ocas-interfaces.md` | Inter-skill intake contracts, cooperative queries, signal formats, handoff paths | 1.4.0 |
| `spec-ocas-journal.md` | Journal format, OKR evaluation, champion/challenger model | 1.2.3 |
| `spec-ocas-ontology.md` | Entity type hierarchy, skill extraction ownership, identity model | 2.3.0 |
| `spec-ocas-shared-schemas.md` | Canonical cross-cutting data schemas and domain extensions | 1.1.4 |
| `spec-ocas-storage-conventions.md` | Storage roots, naming conventions, retention rules | 1.0.3 |
| `spec-ocas-workflow-plans.md` | Workflow plan format, parameter system, expected bundled plans | 1.1.3 |
| `spec-ocas-skill-publishing.md` | README, CHANGELOG, and release structure standard | 1.0 |
| `spec-ocas-scripts.md` | `scripts/` directory best practices: CLI shape, auth, paths, boundary discipline | 1.0.0 |
| `spec-ocas-auth-github.md` | GitHub authentication patterns: env vars, token storage, `gh` CLI, Claude Code OAuth | 1.0.0 |
| `spec-ocas-auth-claude.md` | Claude API authentication patterns: API key, model selection, `claude auth login` runtime flow | 1.0.0 |

## Build Documentation

| File | Description | Version |
|---|---|---|
| `ocas-build-template.md` | Canonical SKILL.md template for new skills | 2.2.0 |
| `ocas-skill-authoring-rules.md` | Rules and conventions for skill authorship | 2.10.0 |

## Active skill repositories (as of 2026-05-19)

| Skill | Repository |
|---|---|
| ocas-forge | `indigokarasu/forge` |
| ocas-rally | `indigokarasu/rally` |
| ocas-scout | `indigokarasu/scout` |
| ocas-sift | `indigokarasu/sift` |
| ocas-look | `indigokarasu/look` |
| ocas-reach | `indigokarasu/reach` |
| ocas-corvus | `indigokarasu/corvus` |
| ocas-elephas | `indigokarasu/elephas` |
| ocas-weave | `indigokarasu/weave` |
| ocas-praxis | `indigokarasu/praxis` |
| ocas-voyage | `indigokarasu/voyage` |
| ocas-sands | `indigokarasu/sands` |
| ocas-custodian | `indigokarasu/custodian` |
| ocas-taste | `indigokarasu/taste` |
| ocas-bower | `indigokarasu/bower` |
| ocas-spot | `indigokarasu/spot` |
| ocas-mentor | `indigokarasu/mentor` |
| ocas-fellow | `indigokarasu/fellow` |
| ocas-vesper | `indigokarasu/vesper` |
| ocas-imagine | `indigokarasu/imagine` |
| ocas-google-workspace | `indigokarasu/google-workspace` |
| ocas-finch | `indigokarasu/ocas-finch` |
| ocas-lucid | `indigokarasu/lucid` |

No active repository (historical reference only): ocas-haiku, ocas-dispatch, ocas-thread, ocas-relay, ocas-multipass, ocas-vibes, ocas-triage. See `spec-ocas-ontology.md` for historical entity extraction mappings.

## Changes

See [CHANGELOG.md](CHANGELOG.md) for a summary of changes by date.

## Private

This repository is private. These specifications are internal design documents for the OCAS system. Do not publish or distribute.
