# SupplyLens AI Module: Architecture & Technical Specification

## Overview
SupplyLens AI is the integrated software and supplier risk intelligence module of **CyberSecureChain**. It operates as a first-class module within the unified FastAPI + React architecture, sharing the database, styling tokens, navigation shell, and digital twin simulation infrastructure.

---

## 1. Relational Database Schema

SupplyLens AI adds 9 core tables to the SQLAlchemy data model (`backend/app/models.py`):

1. **`suppliers`**: Third-party vendor directory tracking name, category (Software, Cloud, Hardware, Logistics), tier (1–3), criticality (1–10), assessment status, and risk level.
2. **`software_projects`**: Enterprise software codebases and applications (e.g. WMS picking service, order processing API, robotics control firmware) linked optionally to physical facilities.
3. **`sbom_import_jobs`**: Ingestion audit log tracking uploaded files, parser format (CycloneDX vs SPDX), parsed component count, extracted relationships, and schema warnings.
4. **`software_components`**: Individual open-source and proprietary software packages ingested from SBOMs. Stores Package URL (PURL), version, inferred ecosystem, license, direct vs transitive scope, and calculated risk score.
5. **`component_dependencies`**: Graph edges representing parent-child dependency trees (`DEPENDS_ON`).
6. **`component_findings`**: Known vulnerabilities (CVEs) affecting components, enriched from OSV.dev and CISA KEV. Stores CVSS scores, remediation fixed versions, and triage lifecycle status.
7. **`component_deployments`**: Cyber-physical bindings linking a software component to a microservice, host cyber asset, operational facility, and business workflow.
8. **`risk_snapshots`**: Point-in-time calculation logs preserving the exact factor breakdown, available factors, missing factors, and calculation rationale for reproducibility.
9. **`mitigation_actions`**: Blue team remediation tracking (e.g. upgrade package, apply network isolation, review supplier SLA).

---

## 2. API Endpoints

SupplyLens AI exposes dedicated endpoints prefixed with `/api/supplylens/`:

| Method | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/api/supplylens/overview` | KPI summary metrics (projects, components, open CVEs, KEV matches) |
| `GET` | `/api/supplylens/projects` | List software projects with component counts |
| `POST` | `/api/supplylens/projects` | Register a new software codebase |
| `POST` | `/api/supplylens/projects/{id}/import-sbom` | Ingest CycloneDX or SPDX JSON manifest |
| `GET` | `/api/supplylens/imports` | History of all SBOM upload jobs |
| `GET` | `/api/supplylens/components` | Search and filter software components |
| `POST` | `/api/supplylens/components/{id}/enrich` | Trigger on-demand OSV.dev vulnerability lookup |
| `GET` | `/api/supplylens/findings` | List all vulnerability findings with triage filters |
| `PATCH`| `/api/supplylens/findings/{id}/status` | Update triage status (`OPEN`, `IN_TRIAGE`, `MITIGATED`, `ACCEPTED`) |
| `GET` | `/api/supplylens/suppliers` | List third-party suppliers and risk scores |
| `POST` | `/api/supplylens/suppliers` | Register a new third-party supplier |
| `GET` | `/api/supplylens/deployments` | List cyber-physical mappings (Component → Facility) |
| `DELETE`| `/api/supplylens/deployments/{id}` | Remove a cyber-physical mapping |
| `GET` | `/api/supplylens/risk/score` | Compute on-demand deterministic risk for any entity |
| `POST` | `/api/supplylens/copilot/query` | Grounded AI Copilot decision support analysis |
| `GET` | `/api/supplylens/reports/findings.csv` | Export complete vulnerability register to CSV |

---

## 3. Frontend Architecture

SupplyLens AI pages reside under `frontend/src/components/supplylens/`:
- `SupplyLensOverview.tsx`: Control tower dashboard with summary cards and recent CVE activity.
- `SbomImports.tsx`: Drag-and-drop file upload, JSON paste editor, and historical ingestion log.
- `ComponentInventory.tsx`: Filterable table with direct/transitive badges and on-demand OSV enrichment.
- `FindingsView.tsx`: CVE triage console with CISA KEV tags, status selectors, and CSV export.
- `SupplierIntelligence.tsx`: Vendor registry, assessment status tracker, and add-supplier form.
- `ExposureMap.tsx`: Visual multi-step propagation chain (`Package → Service → Host → Facility`).
- `AICopilot.tsx`: Grounded decision support interface with pre-built queries and explainable rationales.
- `ScenarioLab.tsx`: Safe What-If lab evaluating software disruption propagation and hardened controls.
