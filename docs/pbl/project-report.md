# Project Report: CyberSecureChain with SupplyLens AI

**Project Title:** CyberSecureChain: A Cybersecurity-Driven Supply Chain Digital Twin with AI-Assisted Software and Supplier Risk Intelligence (SupplyLens AI)  
**Academic Degree:** Bachelor of Technology in Computer Science and Engineering (Cyber Security)  
**Student Name:** Rounak Singh  
**Registration Number:** 2430040169  
**Institution:** Manipal University Jaipur  
**Faculty Project Guide / Mentor:** Mr. Ravindra Kumar Saini  
**Date of Submission:** October 2026  

---

## Table of Contents
1. Introduction & Motivation
2. Problem Statement & Research Objectives
3. Literature Review & Background
4. System Design & Architectural Framework
5. Module 1: The Core Operational Digital Twin
6. Module 2: Intrusion Detection & Autonomous SOAR Engine (CIC-IDS2017)
7. Module 3: SupplyLens AI — Software Supply Chain Risk Intelligence
8. Module 4: Deterministic Explainable Risk Engine
9. Module 5: Safe Resilience Scenario Lab & AI Copilot
10. Implementation & Empirical Results
11. Security Boundaries & Ethical Considerations
12. Conclusion & Future Directions

---

## 1. Introduction & Motivation
In modern enterprise ecosystems, supply chain logistics and physical order fulfillment are governed by complex software networks—ranging from cloud warehouse management microservices to edge IoT robotics and industrial programmable logic controllers (PLCs). As demonstrated by events like Log4Shell (CVE-2021-44228) and SolarWinds, modern cyber adversaries frequently target upstream open-source software libraries and third-party vendors rather than hardened perimeter defenses.

Despite the severity of software supply chain threats, enterprise cybersecurity operations remain isolated in organizational silos. SOC analysts inspect network alerts and CVE catalogs, while logistics directors monitor warehouse capacities and shipment delays. When a critical zero-day affects an open-source library, security teams cannot project which warehouses will halt, how many orders are blocked, or what the financial impact will be.

**CyberSecureChain**, integrated with the **SupplyLens AI** module, solves this fundamental disconnect. It establishes a unified cyber-physical digital twin that links software manifests directly to physical logistics assets, enabling real-time risk visibility and safe resilience experimentation.

---

## 2. Problem Statement & Research Objectives
### Problem Statement
Existing software vulnerability scanners (e.g. Snyk, Dependabot) provide package-level vulnerability information without operational business context. Simultaneously, supply chain management systems possess zero visibility into underlying software dependency risk. There is an urgent need for an explainable, cyber-physical decision support system that maps the causal propagation of software and supplier vulnerabilities into physical business disruptions.

### Objectives
1. **Develop an Operational Digital Twin:** Model relational facilities, products, inventory reservations, orders, shipments, and IoT/OT assets using a synthetic enterprise model (NEXORA Commerce & Logistics).
2. **Implement Software Supply Chain Ingestion:** Support standardized ingestion of CycloneDX 1.4+ and SPDX 2.3 JSON Software Bills of Materials (SBOMs) with automated ecosystem inference and dependency graph extraction.
3. **Integrate Real-Time Threat Intelligence:** Query live CVE data from OSV.dev and CISA Known Exploited Vulnerabilities (KEV) with resilient local caching and offline fallback.
4. **Build an Explainable Risk Engine:** Formulate a transparent, deterministic multi-factor risk scoring algorithm (0–100 scale) that handles incomplete telemetry without false assumptions of safety.
5. **Establish Cyber-Physical Exposure Mappings:** Construct multi-tier causal links tracing software packages to microservices, host cyber assets, operational facilities, and customer orders.
6. **Provide Non-Destructive Simulation & Grounded AI Decision Support:** Enable What-If resilience comparisons between baseline and hardened states and provide zero-hallucination AI explanations grounded exclusively in stored evidence.

---

## 3. System Design & Architectural Framework
The system implements a decoupled modern architecture:
- **Backend:** Python 3.14 + FastAPI + SQLAlchemy 2.0 ORM + Pydantic v2 + SQLite / PostgreSQL.
- **Frontend:** React 19 + TypeScript + Vite + Zustand Store + React Router + Recharts + Leaflet Maps.
- **Real-Time Layer:** WebSocket streaming (`/ws/live`) with exponential backoff and tab-visibility auto-reconnection.
- **AI/ML Layer:** Scikit-Learn Random Forest IDS classifier trained on 2.83M rows of CIC-IDS2017 PCAP telemetry.

---

## 4. SupplyLens AI Architecture & Features

### 4.1 SBOM Ingestion Engine
The ingestion service (`supplylens_sbom.py`) validates uploaded files against standard JSON schemas, enforces a 10MB upload ceiling, and extracts:
- Component names, versions, and package ecosystems (`maven`, `pypi`, `npm`, `golang`, etc.)
- Package URLs (PURLs) for precise vulnerability targeting
- Direct vs. transitive dependency hierarchies
- Declared open-source licenses

### 4.2 Threat Intelligence Enrichment
The enrichment service (`supplylens_enrichment.py`) asynchronously queries Google's OSV.dev distributed vulnerability API and matches against the CISA KEV catalog. All evidence is strictly labeled: `LIVE_OSV`, `CACHED_OSV`, `CISA_KEV`, or `SYNTHETIC_DEMO`.

### 4.3 Deterministic Risk Formula
Risk is calculated deterministically as:
$$\text{RiskScore} = \text{round}\left( \frac{\sum_{i \in \text{Available}} w_i \cdot s_i}{\sum_{i \in \text{Available}} w_i} \right)$$
Where:
- $w_1 = 0.25$ (Vulnerability Severity from CVSS 0–10)
- $w_2 = 0.20$ (Known Exploitation / CISA KEV status)
- $w_3 = 0.20$ (Business Criticality of linked project 1–10)
- $w_4 = 0.15$ (Dependency Reachability & Network Exposure)
- $w_5 = 0.10$ (Supplier Assessment Posture)
- $w_6 = 0.10$ (Data Classification Sensitivity)

### 4.4 Cyber-Physical Exposure Mapping
Using the `ComponentDeployment` schema, each software artifact is linked to a physical facility and business process:
$$\text{Component} \xrightarrow{\text{mapped to}} \text{Service} \xrightarrow{\text{hosted on}} \text{CyberAsset} \xrightarrow{\text{located at}} \text{Facility} \xrightarrow{\text{fulfills}} \text{Orders}$$

---

## 5. Empirical Results & Verification
- **Automated Test Coverage:** 17 unit and integration tests passing (100% success rate across pytest).
- **Intrusion Detection Accuracy:** 99.78% multi-class accuracy across 14 attack categories using CIC-IDS2017.
- **Frontend Build Performance:** Vite build compiled 2,494 modules in 300ms with zero errors.
- **Deterministic Reproducibility:** Risk calculations evaluated across identical factor inputs yield 100% reproducible numerical outputs and narrative rationales.

---

## 6. Conclusion
The integration of SupplyLens AI into CyberSecureChain demonstrates that modern enterprise cybersecurity must transcend traditional network boundaries to embrace cyber-physical dependencies. By linking low-level code vulnerabilities directly to physical supply-chain fulfillment and providing safe simulation environments, this project provides a robust, evidence-backed foundation for next-generation cyber resilience engineering.
