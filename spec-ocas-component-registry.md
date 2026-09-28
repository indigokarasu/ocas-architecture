# OCAS Component Registry

Spec Version: 1.0.0
Author: Indigo Karasu
Status: normative

## Purpose

components.json is the machine-readable source of truth for component lifecycle and architectural ownership.

Architecture prose explains responsibilities but does not independently decide whether a component is active, transitional, planned, support-only, or retired.

## Current status values

active
: Production architecture may depend on the component.

transitional
: Production uses the component, but an explicit migration_obligation exists.

planned
: A normative contract exists but production must not assume the implementation is complete.

support
: The component supports architecture/runtime work but is not a domain owner.

Retired components live in retired_components rather than components.

## Required fields

Current component records include id, type, layer, status, and visibility.

Public repositories are named only when appropriate. Private implementation repositories may remain null while their architectural responsibility is documented.

Transitional records include migration_obligation.

## Privacy

The public registry may describe a private component's responsibility without exposing private implementation details.

## Drift

scripts/validate_architecture.py checks unique ids, lifecycle states, migration obligations, absence of retired dependencies from normative specs, principal/memory separation invariants, and required normative files.

## Restore/bootstrap

Restore tooling should consume this registry or a generated deployment manifest derived from it.

A hardcoded historical skill list is not authoritative and must not reintroduce retired components.

## Change rule

A change that adds or retires a component, changes canonical responsibility, or adds/removes a migration obligation updates components.json in the same architecture change.
