# Technical Viva & Defense Guide

**Student:** Rounak Singh (2430040169) | **Mentor:** Mr. Ravindra Kumar Saini  
**Degree:** B.Tech CSE (Cyber Security) | **Institution:** Manipal University Jaipur  

---

## 1. Executive Summary for Evaluators

**Q: What is the core problem addressed by CyberSecureChain?**  
**A:** In modern enterprise operations, software supply chain risks (e.g. vulnerable third-party OSS packages like Log4j or compromised supplier components) are isolated from physical operational awareness. If a software library in a warehouse picking system is compromised, traditional security tools alert on the CVE, but cannot project how many customer shipments will be delayed or which physical facility will halt. CyberSecureChain bridges this gap by marrying an operational supply-chain digital twin with software bill of materials (SBOM) intelligence and deterministic risk modeling.

---

## 2. Technical Architecture & Defense Questions

### Q1: How does SupplyLens AI ingest and validate software components?
**Answer:**  
SupplyLens AI accepts standard CycloneDX 1.4+ and SPDX 2.3 JSON manifests. The parser (`backend/app/services/supplylens_sbom.py`) validates the JSON structure against strict schemas, enforces a 10MB upload boundary, infers package ecosystems (Maven, PyPI, npm, Golang) from Package URLs (PURLs), and idempotently seeds the components and dependency relationships into relational storage.

### Q2: Why is the risk calculation deterministic instead of relying on an LLM or black-box ML model?
**Answer:**  
For cybersecurity risk governance and safety-critical infrastructure, calculations must be audit-transparent, reproducible, and explainable. The deterministic risk engine (`supplylens_risk.py`) computes a 0–100 score using six weighted factors:
1. Vulnerability Severity (25%)
2. Known Exploitation / CISA KEV (20%)
3. Business Criticality (20%)
4. Dependency Reachability & Exposure (15%)
5. Supplier Posture (10%)
6. Data Sensitivity (10%)
Crucially, missing factors do not default to zero; instead, weights are normalized over available evidence so incomplete telemetry is never silently treated as safety.

### Q3: What is the cyber-physical mapping mechanism?
**Answer:**  
Through the `ComponentDeployment` entity, each software component is explicitly linked to:
- A runtime microservice (`service_name`)
- A host cyber asset (`cyber_asset_id` e.g. `SRV-WMS-01`)
- A physical facility (`facility_id` e.g. Jaipur Distribution Center)
- An operational business process (e.g. Inventory Picking and Sorting)
This allows the system to trace a CVE directly to affected customer orders and calculate simulated downtime and financial loss.

### Q4: How does the IDS Machine Learning model work?
**Answer:**  
The IDS engine uses a Random Forest classifier trained on the genuine CIC-IDS2017 benchmark dataset (2.83M rows across 80 network flow features). During simulations and live packet streaming, network flows are synthesized based on actual attack scenarios (DDoS, Botnet, SQL Injection, Slowloris) and passed to the model, which outputs real-time attack classifications with 99.78% multi-class accuracy.

### Q5: How does the platform ensure safety during attack simulations?
**Answer:**  
All simulations execute within non-destructive in-memory snapshots (`SimulationEngine.compare()` and `/api/cyber/what-if`). The primary operational state (orders, inventory, physical facility status) is never modified or exploited. No packets are sent to external networks, and no external IP addresses or credentials are scan targets.

### Q6: What is the role of the AI Risk Copilot?
**Answer:**  
The AI Risk Copilot (`supplylens_copilot.py`) provides human-readable contextual explanations grounded entirely in the active database state. It operates using a deterministic expert heuristic engine with zero external API key requirements, ensuring zero hallucination and complete reproducibility during demonstrations and evaluations.

---

## 3. Live Demonstration Script for Evaluators (5 Minutes)

1. **Step 1: Admin Operations Control Tower (1 min)**
   - Open `/admin/overview`
   - Show physical facilities on the Leaflet map (Delhi, Mumbai, Bengaluru, Jaipur)
   - Show active orders, inventory batches, and shipment fleet tracking
2. **Step 2: Cyber Resilience Center (1 min)**
   - Open `/cyber/security-overview`
   - Show asset vulnerability posture (posture score / 100)
   - Open `/cyber/auto-defense` and observe live network packet stream
3. **Step 3: SupplyLens AI — Software Supply Chain (1.5 min)**
   - Open `/supplylens/sl-overview` to view overall software risk KPIs
   - Open `/supplylens/components` and click "OSV Enrich" on `log4j-core` to show live OSV.dev lookup
   - Open `/supplylens/exposure-map` to show the propagation chain: `log4j-core → WMS-PickPack → SRV-WMS-01 → FC-DEL-01 → Orders`
4. **Step 4: Scenario Lab & AI Copilot (1.5 min)**
   - Open `/supplylens/scenario-lab`
   - Select "Upstream Supplier Package Tampering" and click "Evaluate Scenario"
   - Show the comparative table: 8 compromised assets & ₹4.2M loss in baseline vs 1 compromised asset & ₹0 loss in hardened state
   - Open `/supplylens/ai-copilot` and submit a query: "Explain the operational risk of Log4Shell on fulfillment centers"
   - Show instant, evidence-grounded response with recommended remediations
