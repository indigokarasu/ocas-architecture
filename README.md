# ocas-architecture

<p align="center">
  <img src="./assets/readme/hero.jpg" width="100%" alt="OCAS system architecture specifications, schemas, and design documents">
</p>

Normative architecture, schemas, runtime contracts, and validation for the OCAS agent suite.

## Current architecture

OCAS v2 uses Chronicle as the principal-scoped durable memory/context substrate.

User memory and agent autobiographical identity are separate ownership domains. User Dreaming consolidates knowledge about the user only; the agent's autobiographical growth system remains independent.

The canonical component lifecycle registry is components.json.

## Normative contracts

- spec-ocas-architecture.md — system model and invariants
- spec-ocas-component-registry.md — component lifecycle and drift semantics
- spec-ocas-principals-and-memory-boundaries.md — user/agent ownership, correction, retraction and privacy erasure
- spec-ocas-user-dreaming.md — user-only offline consolidation
- spec-ocas-dreaming.md — cross-domain boundary map for user Dreaming, agent growth and system improvement
- spec-ocas-runtime-contracts.md — capabilities, credentials, task contracts, provenance, artifact gates and introspection
- spec-ocas-interfaces.md — typed cross-component communication
- spec-ocas-storage-conventions.md — private state, journals, queues, exports and runtime-owned storage
- spec-ocas-shared-schemas.md — canonical cross-component objects
- spec-ocas-journal.md — immutable run/evaluation evidence
- spec-ocas-recovery.md — durable intent, leases, evidence, repair and verified completion
- spec-ocas-workflow-plans.md — durable multi-step workflows
- spec-ocas-skill-improvements.md — evaluation and evolution standards
- ocas-skill-authoring-rules.md — authoring constraints
- ocas-build-template.md — implementation template

## Key invariants

- Every durable personal-memory write has an explicit principal.
- Evidence may be shared across authorized domains; derived identity may not be conflated.
- User Dreaming never writes agent identity/autobiography.
- Agent autobiographical growth never writes user-owned beliefs.
- Component-private data directories/databases are not APIs.
- Journals are immutable evidence, not automatically durable memory.
- Side-effect completion requires verified postconditions.
- Retired components remain registry history, never active dependencies.

## Validation

Validate this architecture repository:

~~~bash
python3 scripts/validate_architecture.py
~~~

Audit checked-out Indigo repositories for active references to retired systems:

~~~bash
python3 scripts/audit_legacy_references.py --workspace ~/src
~~~

Or audit every repository visible to an authenticated GitHub CLI session:

~~~bash
python3 scripts/audit_legacy_references.py --owner indigokarasu
~~~

The cross-repo audit deliberately excludes preserved historical journals and quarantined retired-component state. Those remain evidence; active code, config, cron, interfaces, and operational documentation may not depend on retired systems.

CI runs the architecture-local validator on pushes and pull requests. The organization-wide audit requires credentials that can read private repositories, so it is run from an authenticated operator/maintenance environment rather than relying on a public-repository Actions token.

## Migration state

components.json may mark live components transitional when their implementation still carries a legacy contract. Transitional state requires an explicit migration_obligation; it does not make the legacy contract normative.

## License

MIT License.
