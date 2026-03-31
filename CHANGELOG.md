# CHANGELOG

All notable changes to OCAS architecture specifications are documented here.

Format: `[spec-file] vX.Y — description`

---

## 2026-03-31

### spec-ocas-ontology.md v1.4
- Added ocas-elephas, ocas-mentor, ocas-praxis, ocas-forge, ocas-fellow, and ocas-custodian to Skill Entity Extraction Ownership table
- Added corresponding entries to Signal Emission Responsibilities table
- Completed skill inventory coverage for all 22 OCAS system skills

---

## 2026-03-30

### spec-ocas-interfaces.md v1.3
- Added Rally → Vesper Portfolio Outcome cooperative read interface
- Added Vesper → Dispatch Briefing Delivery session-scoped interface
- Added Cooperative Query Interfaces section (Sift↔Thread, Sift↔Weave, Scout↔Weave, Taste↔Sift, Voyage↔Sift)
- Added Rally and Vesper to polling cadence table

### spec-ocas-ontology.md v1.2
- Added Skill Entity Extraction Ownership table
- Added Signal Emission Responsibilities table
- Updated Usage by Skills section with explicit per-skill entity type assignments

### spec-ocas-shared-schemas.md v1.3
- Added PortfolioOutcomeRecord schema (Rally domain extension)
- Added ConsumptionSignal and ItemRecord schemas (Taste domain extensions)
- Added EvaluationResult schema (Mentor domain extension)

### ocas-skill-authoring-rules.md v2.4.0
- Added Variant Naming Convention section (format: `{skill-id}-variant-{YYYYMMDD}`)
- Standardized HEARTBEAT.md registration language
- Added ocas-custodian to responsibility boundaries list
- Added Ontology Mapping to required SKILL.md sections for system skills
- Added Bundled Workflow Plans section with expected plan table

### spec-ocas-workflow-plans.md v1.1
- Added Expected Bundled Plans section
- Added plan init registration pattern
- Added notes on graceful skill-absent handling in plan runs

---

## Prior

See git log for individual spec history before this date.
