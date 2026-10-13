# Project Abstract

**Project Title:** CyberSecureChain: A Cybersecurity-Driven Supply Chain Digital Twin with AI-Assisted Software and Supplier Risk Intelligence (SupplyLens AI)  
**Student Name:** Rounak Singh  
**Registration Number:** 2430040169  
**Degree / Specialization:** B.Tech Computer Science and Engineering (Cyber Security)  
**Institution:** Manipal University Jaipur  
**Faculty Project Guide / Mentor:** Mr. Ravindra Kumar Saini  

---

## Abstract

Modern global supply chains have become increasingly interconnected cyber-physical ecosystems where operational resilience is critically dependent on software integrity and third-party supplier security. Recent high-profile cyber incidents—including the Log4Shell crisis, SolarWinds supply-chain breach, and 3CX desktop software compromise—demonstrate that vulnerabilities in low-level third-party software packages and upstream vendor integrations can rapidly propagate into devastating operational outages, warehouse halts, and massive financial losses. However, conventional cybersecurity tools focus exclusively on isolated network telemetry or static software bill of materials (SBOM) scanning, completely disconnected from physical supply-chain state, logistics flows, and business consequence.

To address this gap, this Project-Based Learning (PBL) work introduces **CyberSecureChain** integrated with **SupplyLens AI**—a unified, full-stack cyber-physical supply-chain digital twin that models how software dependencies, vendor security postures, and network anomalies propagate into physical operations. The platform integrates:
1. **Operational Digital Twin:** Models physical facilities (warehouses, fulfillment centers, distribution hubs), inventory stock, customer orders, fleet vehicles with GPS integrity, and OT/IoT automation machinery.
2. **Software Supply Chain Intelligence (SupplyLens AI):** Standardized ingestion of CycloneDX and SPDX JSON SBOM manifests, automated dependency graph resolution, and real-time vulnerability enrichment querying the OSV.dev database and CISA Known Exploited Vulnerabilities (KEV) catalog.
3. **Transparent Explainable Risk Engine:** A deterministic, multi-factor risk calculation framework (0–100 scale) accounting for vulnerability severity, active weaponization (CISA KEV), business asset criticality, dependency reachability, supplier assurance, and data sensitivity—avoiding opaque black-box scoring.
4. **Cyber-Physical Exposure Mapping:** Multi-tier propagation mapping establishing direct causal chains: `Software Package → Runtime Microservice → Host Cyber Asset → Operational Facility → Customer Orders`.
5. **Real-Time Intrusion Detection & Autonomous SOAR:** A Random Forest ML classifier trained on the CIC-IDS2017 dataset (2.83M network flows across 80 extracted features) integrated with an autonomous adversary simulation engine and SOAR automated defense playbooks.
6. **Resilience What-If Lab & Grounded AI Copilot:** Controlled simulation environments comparing vulnerable baseline states against hardened configurations without mutating primary operational twin state, supported by a zero-hallucination, deterministic AI Risk Copilot.

The platform is fully implemented using FastAPI, SQLAlchemy, SQLite/PostgreSQL, React, TypeScript, Vite, and Leaflet, complete with unit and integration test coverage and safe synthetic data labeling. The system serves as a decision-support and educational prototype demonstrating cyber-physical risk visibility for critical infrastructure.
