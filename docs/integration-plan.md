# CyberSecureChain & SupplyLens AI Integration Plan

## Project Identity & Academic Context
- **Academic Project Title**: CyberSecureChain: A Cybersecurity-Driven Supply Chain Digital Twin with AI-Assisted Software and Supplier Risk Intelligence
- **Integrated Module**: SupplyLens AI (Software & Supplier Risk Intelligence Layer)
- **Institution**: Manipal University Jaipur
- **Programme**: B.Tech CSE (Cybersecurity)
- **Student**: Rounak Singh (Reg No: 2430040169)
- **Project Type**: University Project-Based Learning (PBL) & Cybersecurity Portfolio

---

## 1. Baseline Audit & Pre-Integration Verification
- **Backend**: FastAPI + SQLAlchemy + SQLite (`cybersecurechain.db`) / PostgreSQL support.
- **Frontend**: React 18, TypeScript, Vite, React Router, Zustand, Recharts, Leaflet, Lucide icons.
- **Baseline Tests**: 6/6 tests passing (`test_autonomous.py`, `test_domain.py`).
- **Baseline Build**: Vite client build passed cleanly (zero errors, 16.31s).
- **Secret Hygiene**: `.gitignore` updated to strictly exclude `.env*`, `.vercel`, `*.tsbuildinfo`, while preserving `.env.example`. No secrets committed.

---

## 2. Integrated Product Architecture
SupplyLens AI is integrated **directly inside the existing CyberSecureChain application shell** as a first-class intelligence layer, not as a disjoint second app.

```
                    ┌────────────────────────────────────────────────────────┐
                    │               CyberSecureChain Application             │
                    │                   Unified UI & Navigation              │
                    └───────────────────────────┬────────────────────────────┘
                                                │
         ┌──────────────────────────────────────┼──────────────────────────────────────┐
         ▼                                      ▼                                      ▼
┌──────────────────┐                  ┌──────────────────┐                  ┌──────────────────┐
│    Operations    │                  │ Cyber Resilience │                  │  SupplyLens AI   │
│  (Admin Tower)   │                  │   (SOC Center)   │                  │ (Software/Vendor)│
├──────────────────┤                  ├──────────────────┤                  ├──────────────────┤
│• Facilities      │                  │• Auto Defense    │                  │• Overview & KPIs │
│• Inventory       │                  │• Security Map    │                  │• SBOM Ingestion  │
│• Orders & Fleet  │                  │• ML IDS (80-feat)│                  │• Dependency Graph│
│• IoT / OT Twin   │                  │• Incident Ops    │                  │• Vulnerabilities │
│• Physical Flow   │                  │• Safe Simulation │                  │• Supplier Regis. │
│• Digital Twin    │                  │• What-If Control │                  │• Cyber-Physical  │
│• Unified Events  │                  │• Resilience Score│                  │  Exposure Map    │
└────────┬─────────┘                  └────────┬─────────┘                  │• AI Risk Copilot │
         │                                     │                            │• Scenario Lab    │
         │                                     │                            │• Export Reports  │
         │                                     │                            └────────┬─────────┘
         └─────────────────────────────────────┴─────────────────────────────────────┘
                                                │
                                    ┌───────────────────────┐
                                    │ Unified DB & Services │
                                    │ • SQLAlchemy ORM      │
                                    │ • Deterministic Risk  │
                                    │ • OSV/CISA/KEV Cache  │
                                    │ • Event Audit Trail   │
                                    │ • Safe Sim Engine     │
                                    └───────────────────────┘
```

---

## 3. Implementation Phases
- **Phase 0 — Audit & Baseline**: ✅ Completed (tests 6/6, build verified, gitignore hardened).
- **Phase 1 — Design & Data Model**: Models specification, mapping definitions, documentation.
- **Phase 2 — Backend Foundations**: SQLAlchemy tables (`software_projects`, `software_components`, `component_dependencies`, `suppliers`, `component_findings`, `component_deployments`, `risk_snapshots`, `mitigation_actions`), SBOM parsers (CycloneDX & SPDX JSON), validation, migrations.
- **Phase 3 — Intelligence Services**: OSV.dev & CISA KEV clients with timeout, retry, cache, transparent deterministic risk scoring engine (0-100 explainable formula).
- **Phase 4 — Cyber-Physical Mapping**: Linking components/suppliers to services, cyber assets, facilities, and business processes.
- **Phase 5 — Safe Simulation Integration**: Software & supplier failure scenarios extending `SimulationEngine` and `WhatIf` comparisons.
- **Phase 6 — Frontend Experience**: SupplyLens views inside unified shell: Overview, SBOM Imports, Components, Dependency Graph, Findings, Supplier Intelligence, Exposure Map, Scenario Lab, Reports, Methodology.
- **Phase 7 — AI Risk Copilot & Reports**: Context-aware grounded explanations with deterministic non-LLM fallback; real CSV and print-to-PDF report generation.
- **Phase 8 — Quality & Verification**: Automated unit & integration tests, full build validation, secret audit.
- **Phase 9 — Academic Documentation**: Comprehensive PBL report, abstract, architecture, testing results, viva preparation guide.
