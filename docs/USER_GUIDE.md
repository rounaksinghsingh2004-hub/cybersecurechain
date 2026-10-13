# CyberSecureChain — Complete Step-by-Step User Guide

> **Project:** CyberSecureChain: A Cybersecurity-Driven Supply Chain Digital Twin with AI-Assisted Software and Supplier Risk Intelligence  
> **Student:** Rounak Singh (Reg: 2430040169) · B.Tech CSE (Cyber Security) · Manipal University Jaipur  
> **Guide & Mentor:** Mr. Ravindra Kumar Saini  
> **Live Production App:** https://frontend-mauve-chi-80.vercel.app  
> **Live Backend API:** https://cybersecurechain-api.onrender.com  
> **Repository:** https://github.com/rounaksinghsingh2004-hub/cybersecurechain  

---

## Table of Contents

1. [Getting Started — Opening the App](#1-getting-started)
2. [Operations Mode — Admin View](#2-operations-mode)
3. [Cyber Resilience & SupplyLens AI Mode (7 Unified Modules)](#3-cyber-resilience--supplylens-ai-mode)
   - [Module 1: ⚡ Auto Defense](#module-1--auto-defense)
   - [Module 2: 🛡️ Command Center](#module-2-️-command-center)
   - [Module 3: 🔍 Vulnerabilities & Findings](#module-3--vulnerabilities--findings)
   - [Module 4: 🗺️ Attack Surface & Exposure](#module-4-️-attack-surface--exposure)
   - [Module 5: 🧪 Simulation & Scenario Lab](#module-5--simulation--scenario-lab)
   - [Module 6: 📦 Software & Supplier Inventory](#module-6--software--supplier-inventory)
   - [Module 7: 🤖 AI Risk Copilot](#module-7--ai-risk-copilot)
4. [Live Attack Simulation (Red vs Blue Cycle)](#4-live-attack-simulation)
5. [SBOM Ingestion Step-by-Step Walkthrough](#5-sbom-ingestion-walkthrough)
6. [AI Risk Copilot Usage Guide](#6-ai-risk-copilot-usage-guide)
7. [API & Direct Backend Documentation](#7-api--direct-backend-documentation)
8. [Running Locally](#8-running-locally)
9. [Evaluator Demo & Viva Checklist](#9-evaluator-demo--viva-checklist)
10. [Appendix: Architecture & Tech Stack](#10-appendix-architecture--tech-stack)

---

## 1. Getting Started

### Step 1.1 — Open the Application

Open your browser and navigate to:

```
https://frontend-mauve-chi-80.vercel.app
```

> **First load note (Render free tier):** If the backend has been dormant, the initial API call takes ~20–30 seconds for the free container to boot. Once loaded, all twin state, metrics, and risk charts populate automatically.

### Step 1.2 — Understand the Two Balanced Navigation Modes

At the top-left of the sidebar you will see two balanced mode-switch buttons:

| Button | Mode | Key Role |
|---|---|---|
| **ADMIN** | Operations Control Tower | Supply chain physical twin — facilities, inventory, products, orders, shipments, fleet, employees, machines, IoT & OT assets |
| **CYBER** | Cyber Resilience & SupplyLens AI | Complete cybersecurity & software supply chain defense suite consolidated into **7 high-impact tabbed modules** |

Click either button to toggle views. In **CYBER** mode, the sidebar fits on any standard screen without vertical scrolling.

### Step 1.3 — Real-Time Live Feed & WebSocket Indicator

- **Bottom-left status dot:** Indicates live connection to the backend ML scanner (`IDS ML · LIVE`).
- **Live Feed ticker:** Real-time stream of synthetic adversary traffic injections, Random Forest classification detections, and SOAR mitigation events.
- **Top-right indicator:** Shows WebSocket status (`LIVE` / `OFFLINE`), active alerts, and a **Reset Demo** trigger.

---

## 2. Operations Mode

> **Mode button:** ADMIN | **Default URL:** `/admin/overview`

### Step 2.1 — Overview Dashboard

**URL:** `/admin/overview`

**What you see:**
- **KPI cards:** Active orders, physical inventory units, modelled shipments, and connected India network facilities.
- **Bar chart:** Order pipeline by status (PENDING, PROCESSING, SHIPPED, DELIVERED).
- **Activity log:** Real-time event stream of supply-chain operations.
- **Interactive Leaflet Map:** All NEXORA facility locations across India. Click any marker to open the quick-inspect drawer.
- **Simulate Live Attack panel:** Dropdown to manually pick a facility (e.g., WH-MUMBAI-01) and inject a 60-second attack to test the system in real time.

---

### Step 2.2 — Supply Chain / Digital Twin

**URL:** `/admin/digital-twin`

Displays the connected relational network graph: Factory → Warehouse → Distribution Center → Customer Hub. Toggle tabs: `Physical`, `Logistics`, `Cyber`, or `Combined` to inspect multi-layer dependency edges.

---

### Step 2.3 — Operational Registers

| Page | URL | Description |
|---|---|---|
| **Facilities** | `/admin/facilities` | Facility code, type, city location, operational status, capacity. |
| **Inventory** | `/admin/inventory` | SKU, product name, facility, available units, reserved units, and **quarantined units** (stock locked by security controls). |
| **Products** | `/admin/products` | Master product catalog with suppliers and manufacturing sites. |
| **Orders** | `/admin/orders` | Order number, customer, origin, destination, lifecycle status, and **Cyber status** (`NORMAL` vs `DISRUPTED`). |
| **Shipments** | `/admin/shipments` | In-transit tracking, assigned vehicle, delivery status, and **GPS Integrity** (`VERIFIED` vs `SPOOFED`). |
| **Fleet** | `/admin/fleet` | Fleet GPS telemetry map with route integrity checks. |
| **Employees** | `/admin/employees` | Personnel directory with MFA enforcement and account lockout status. |
| **Machines & Robots** | `/admin/machines-&-robots` | Physical warehouse automation robots, PLCs, zone, and cyber compromise state. |
| **IoT & OT** | `/admin/iot-&-ot` | Sensor networks, IoT gateways, OT network segments, and telemetry status. |

---

## 3. Cyber Resilience & SupplyLens AI Mode

> **Mode button:** CYBER | **Default URL:** `/cyber/command-center`

The Cyber view consolidates all operational resilience and software supply chain capabilities into **7 clean tabbed modules**:

---

### Module 1: ⚡ Auto Defense

**URL:** `/cyber/auto-defense`

The centerpiece of the autonomous digital twin. Demonstrates self-defending cyber-physical resilience without human intervention:

1. **Adversary AI Engine (Left Column):** Autonomous attacker launches real attack signatures (CIC-IDS2017 attack classes including PortScan, DDoS LOIC/HOIC, Infiltration, Brute Force, Web Attacks).
2. **CIC-IDS2017 ML Classifier (Middle Column):** Real-time 80-feature Random Forest model (99.78% multi-class accuracy) inspects traffic features and outputs attack probability and threat class.
3. **SOAR Autonomous Defender (Right Column):** Automatically isolates compromised OT/IT assets, reroutes pending orders to alternate regional warehouses, and broadcasts mitigation events.
4. **Lifecycle Stages:** `RECON` → `ATTACK_IN_PROGRESS` → `ML_IDS_DETECTED` → `MITIGATED`.

---

### Module 2: 🛡️ Command Center

**URL:** `/cyber/command-center`

The executive oversight dashboard consolidating organizational cyber posture and software risk into 4 sub-tabs:

#### Tab 1: Enterprise Cyber Posture
- Global posture score (0–100 calculated from asset exposure and control coverage).
- Critical asset count (criticality ≥ 8), high-risk assets, and active incidents.
- Bar chart of asset risk distribution (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- Cyber asset inventory table with clickable rows to inspect host metadata.

#### Tab 2: Software Supply Chain Posture
- High-level SupplyLens AI metrics: total projects, open-source components, registered suppliers, CVE findings, CISA KEV count, and cyber-physical mappings.
- Average component risk score (deterministic 0–100).
- Recent vulnerability triage highlights.

#### Tab 3: Controls & Resilience
- **Resilience Score (0–100):** Derived from detection capability, containment capability, recovery capability, and identity resilience.
- **Blue Team Controls:** Interactive toggles to enable/disable MFA, Network Segmentation, Automated Backups, and IDS Sensor Monitoring.

#### Tab 4: Incident Operations & Audit
- Active incident cards with one-click containment action dropdowns (e.g., `ISOLATE_ASSET`, `DISABLE_ACCOUNT`, `APPLY_SEGMENTATION`).
- Resolved incident history log with timestamps and containment notes.
- Unified chronological event timeline.

---

### Module 3: 🔍 Vulnerabilities & Findings

**URL:** `/cyber/vulnerabilities`

Unified vulnerability intelligence across both software dependencies and physical hosts:

#### Tab 1: Software & Package CVEs (SupplyLens Findings)
- Full triage table of software vulnerability findings:
  - Vulnerability ID (e.g., CVE-2021-44228 Log4Shell, CVE-2022-22965 Spring4Shell).
  - Component name & affected version.
  - Severity badge (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  - CVSS score (0.0–10.0).
  - **CISA KEV badge:** Red alert badge indicating confirmed active exploitation in the wild.
  - Status dropdown (`OPEN`, `IN_TRIAGE`, `MITIGATED`, `ACCEPTED`) — saves directly to the database.
  - Fixed version recommendation.
- **Filter by Severity & Status:** Real-time dropdown filters.
- **Export CSV:** One-click download of all findings for compliance reporting (`/api/supplylens/reports/findings.csv`).

#### Tab 2: Host & Infrastructure Weaknesses
- Host-level vulnerabilities mapped to physical servers, OT PLCs, and IoT gateways with recommended mitigation controls.

---

### Module 4: 🗺️ Attack Surface & Exposure

**URL:** `/cyber/exposure`

The critical differentiator connecting software dependencies to physical supply chain disruption:

#### Tab 1: Cyber-Physical Exposure Map
- Visualizes the 5-tier propagation chain:
  $$\text{Package (CVE)} \longrightarrow \text{Service} \longrightarrow \text{Host Asset} \longrightarrow \text{Physical Facility} \longrightarrow \text{Customer Orders}$$
- Columns: Component, Deployed Service Name, Business Process, Mapping Type (`VERIFIED`, `INFERRED`, `USER_MAPPED`), Target Facility, Host Cyber Asset.
- Interactive row drawer: Click any row to trace how an open-source library vulnerability directly endangers warehouse fulfillment and pending customer shipments.
- Delete or create new deployment mappings dynamically.

#### Tab 2: Host Attack Surface & Lateral Paths
- External exposure registry and multi-hop lateral movement attack paths illustrating how attackers pivot from web perimeter into internal OT networks.

---

### Module 5: 🧪 Simulation & Scenario Lab

**URL:** `/cyber/simulation-lab`

Comprehensive "what-if" testing suite with 3 specialized engines:

#### Tab 1: Supply Chain Scenario Lab
- Simulates upstream software and vendor crises:
  - `VENDOR_BANKRUPTCY` — Upstream SaaS/library provider dissolves.
  - `CRITICAL_CVE_EXPLOIT` — Active zero-day exploitation against warehouse controllers.
  - `SBOM_SUPPLY_CHAIN_ATTACK` — Upstream dependency tampering (SolarWinds style).
  - `MASS_PATCHING_DOWNTIME` — Emergency maintenance operational impact.
- Side-by-side comparison: Baseline vs Hardened state (orders at risk, recovery hours, revenue exposure, recommended controls).

#### Tab 2: What-If Facility Resilience
- Side-by-side impact projection for physical facilities:
  - Compares Current Environment vs Hardened Environment.
  - Projected metrics: Assets reached, orders disrupted, shipments delayed, downtime minutes, revenue loss.

#### Tab 3: Direct Disruption Stress Test
- On-demand facility disruption simulator. Pick a scenario (`ACCOUNT_COMPROMISE`, `OT_DISRUPTION`, `RANSOMWARE_IMPACT`), select a target asset, and watch step-by-step killchain propagation with containment boundary identification.

---

### Module 6: 📦 Software & Supplier Inventory

**URL:** `/cyber/inventory`

Single pane of glass for all upstream code and third-party vendor assets:

#### Tab 1: Software Components (SBOM Inventory)
- Full inventory of all open-source libraries parsed from project SBOMs.
- Displays Name, Version, Ecosystem (npm, PyPI, Maven, Go, Cargo), PURL, Direct/Transitive flag.
- **Deterministic Risk Score (0–100):** Transparent multi-factor calculation.
- **OSV Enrich Button:** Click on any component to trigger an on-demand live API query to OSV.dev and CISA KEV to retrieve the latest known vulnerabilities.

#### Tab 2: Supplier Intelligence Register
- Vendor directory with Tier classification (`TIER_1`, `TIER_2`, `TIER_3`), Criticality rating (1–10), and Data Sensitivity (`HIGH`, `MEDIUM`, `LOW`).
- Assessment status tracking (`ASSESSED`, `UNDER_REVIEW`, `PENDING_REVIEW`).
- **Add Supplier Modal:** Form to register new third-party vendors with instant risk calculation.

#### Tab 3: Import SBOM Manifests
- Ingest Software Bill of Materials documents in CycloneDX 1.4+ JSON or SPDX 2.3 JSON formats via file upload or raw JSON pasting.

---

### Module 7: 🤖 AI Risk Copilot

**URL:** `/cyber/ai-copilot`

Grounded AI decision-support assistant designed for security analysts and supply chain officers:

- **Evidence-Grounded Answers:** Answers queries strictly using database records — zero hallucinations.
- **Deterministic Heuristics:** Fully functional without requiring paid external LLM API keys (with optional LLM enhancement when configured).
- **Structured Output:** Each response includes the direct answer, evidence citations, derivation methodology, and confidence assessment.
- **Sample Queries:**
  - *"What are the most critical CVEs currently in the system?"*
  - *"Which software components are deployed at WH-MUMBAI-01?"*
  - *"How many CISA KEV findings remain unmitigated?"*
  - *"Explain the cyber-physical exposure path for Log4Shell."*
  - *"Which suppliers have a pending security assessment?"*

---

## 4. Live Attack Simulation

### 4.1 Autonomous Cycle (Automatic Red vs Blue)

1. Navigate to **CYBER → Auto Defense** (`/cyber/auto-defense`).
2. The autonomous adversarial engine cycles automatically every ~15–30 seconds.
3. Observe the stage transition badges:
   - `RECON` — Port scanning and service discovery.
   - `ATTACK_IN_PROGRESS` — Malicious PCAP injection into facility network.
   - `ML_IDS_DETECTED` — 80-feature Random Forest model classifies attack type with confidence.
   - `MITIGATED` — SOAR playbooks isolate target asset and reroute affected orders.

### 4.2 Manual Live Attack Injection

1. Switch to **ADMIN** mode (`/admin/overview`).
2. Scroll to the **Simulate Live Attack** panel.
3. Select a target facility (e.g., `WH-MUMBAI-01`) and an attack scenario (e.g., `RANSOMWARE_IMPACT`).
4. Click **Inject Attack (60s)**.
5. Notice:
   - Entire application shell activates a red alert overlay with live damage counter (₹ damage/sec).
   - Facility status degrades to `COMPROMISED`.
   - Affected orders in `/admin/orders` change to `cyber_status: DISRUPTED`.
6. Switch to **CYBER → Auto Defense** — watch the ML detector flag the traffic and SOAR auto-recover the facility.
7. Click **Clear** at any time to manually terminate the injection.

---

## 5. SBOM Ingestion Walkthrough

### Step-by-Step Procedure:

1. In the sidebar, select **CYBER → Software & Supplier Inventory** (`/cyber/inventory`).
2. Click the **Import SBOM Manifests** tab.
3. Select an existing project from the dropdown (e.g., `NEXORA-WMS`) or create a new project.
4. Select format: **CycloneDX 1.4+ JSON** or **SPDX 2.3 JSON**.
5. Switch to the **Paste JSON** tab and paste the following valid sample CycloneDX manifest:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "components": [
    {
      "type": "library",
      "name": "requests",
      "version": "2.28.0",
      "purl": "pkg:pypi/requests@2.28.0"
    },
    {
      "type": "library",
      "name": "log4j-core",
      "version": "2.14.1",
      "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"
    }
  ]
}
```

6. Click **Import SBOM**.
7. The parser validates the payload, extracts PURL identifiers, infers ecosystem types, and stores records in the database.
8. Switch to the **Software Components** tab to view the newly ingested packages.
9. Click **OSV Enrich** on `log4j-core` — observe live query results adding CVE-2021-44228 to the findings database.

---

## 6. AI Risk Copilot Usage Guide

1. Navigate to **CYBER → AI Risk Copilot** (`/cyber/ai-copilot`).
2. Type any plain-language risk query in the prompt box:
   - *"Which suppliers are classified as Tier 1?"*
   - *"List all components with a risk score greater than 70."*
   - *"What physical facilities are vulnerable to Text4Shell?"*
3. Click **Ask Copilot**.
4. Review the structured output:
   - **Answer:** Direct factual synthesis from stored database records.
   - **Evidence:** Exact component IDs, vulnerability records, and supplier tiers used.
   - **Methodology:** Transparent calculation note (`deterministic-grounded-v1`).
   - **Confidence:** Evidence completeness rating.

---

## 7. API & Direct Backend Documentation

FastAPI provides interactive Swagger documentation at:

```
https://cybersecurechain-api.onrender.com/docs
```

### Core REST Endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/digital-twin` | Complete digital twin state (facilities, metrics, events) |
| `GET` | `/api/facilities` | Facility status, capacity, and coordinates |
| `GET` | `/api/orders` | Orders with operational and cyber status |
| `GET` | `/api/cyber/overview` | Enterprise posture score and risk breakdown |
| `GET` | `/api/cyber/auto-defense/status` | Autonomous engine campaign state and ML detections |
| `POST` | `/api/cyber/auto-defense/trigger-defense` | Force SOAR auto-mitigation playbook |
| `GET` | `/api/supplylens/overview` | SupplyLens AI KPIs and metrics |
| `GET` | `/api/supplylens/components` | All software components with risk scores |
| `POST` | `/api/supplylens/components/{id}/enrich` | Live OSV.dev and CISA KEV query |
| `GET` | `/api/supplylens/findings` | Vulnerability findings with status and severity filters |
| `PATCH` | `/api/supplylens/findings/{id}/status` | Triage finding status (`OPEN`, `IN_TRIAGE`, `MITIGATED`) |
| `GET` | `/api/supplylens/suppliers` | Third-party supplier registry |
| `POST` | `/api/supplylens/suppliers` | Register new supplier |
| `GET` | `/api/supplylens/deployments` | Cyber-physical exposure mappings |
| `POST` | `/api/supplylens/projects/{id}/import-sbom` | Ingest CycloneDX or SPDX SBOM |
| `POST` | `/api/supplylens/copilot/query` | Grounded AI Copilot decision support |
| `GET` | `/api/supplylens/reports/findings.csv` | Export findings as CSV |

---

## 8. Running Locally

### Prerequisites:
- Python 3.11+
- Node.js 20+

### Step 8.1 — Start Backend:
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API runs at `http://127.0.0.1:8000` (Swagger UI at `/docs`).

### Step 8.2 — Start Frontend:
```powershell
cd frontend
npm install
npm run dev
```
UI runs at `http://localhost:5173`.

### Step 8.3 — Run Test Suite:
```powershell
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -v
```
**Expected outcome:** 17/17 tests passed (100%).

---

## 9. Evaluator Demo & Viva Checklist

Use this structured sequence during faculty evaluation or viva:

- [ ] **1. Introduction & Positioning:** State project title: *CyberSecureChain: A Cybersecurity-Driven Supply Chain Digital Twin with AI-Assisted Software and Supplier Risk Intelligence*. Explain that it connects upstream software vulnerabilities directly to downstream physical warehouse disruption.
- [ ] **2. Operations Twin Demonstration:**
  - Open `/admin/overview` — show dynamic KPI cards and Leaflet India network map.
  - Open `/admin/orders` — point out the `cyber_status` column.
- [ ] **3. Autonomous Self-Defending Twin:**
  - Navigate to `/cyber/auto-defense`.
  - Explain the 3 columns: Adversary AI → 80-feature Random Forest ML (CIC-IDS2017) → SOAR order rerouting.
  - Watch a full autonomous attack cycle complete.
- [ ] **4. Manual Attack Stress Test:**
  - Go to `/admin/overview` and trigger a live attack injection on `WH-MUMBAI-01`.
  - Show the financial damage counter (₹/sec) in the overlay.
  - Show orders getting disrupted, then returning to normal once SOAR mitigates.
- [ ] **5. Streamlined 7-Module Architecture:**
  - Show the clean sidebar under CYBER without vertical scrolling.
  - Open `/cyber/command-center` — toggle through the 4 executive tabs.
- [ ] **6. Vulnerability Intelligence & Triage:**
  - Open `/cyber/vulnerabilities`.
  - Highlight CISA KEV badges on Log4Shell and Spring4Shell.
  - Change status from `OPEN` to `IN_TRIAGE` (shows instant database persist).
  - Click **Download CSV** to demonstrate compliance export.
- [ ] **7. Cyber-Physical Exposure Propagation:**
  - Open `/cyber/exposure`.
  - Trace `log4j-core 2.14.1` → `WMS Order Service` → `SRV-WMS-01` → `WH-MUMBAI-01` → `Affected Orders`.
- [ ] **8. SBOM Ingestion & Live Threat Enrichment:**
  - Open `/cyber/inventory` → **Import SBOM Manifests**.
  - Paste the sample CycloneDX JSON and import.
  - Switch to **Software Components** tab and click **OSV Enrich** to demonstrate live vulnerability lookup.
- [ ] **9. Grounded AI Risk Copilot:**
  - Open `/cyber/ai-copilot`.
  - Ask: *"Which CISA KEV findings are open?"*
  - Explain that responses are derived deterministically from database records without hallucination.
- [ ] **10. Technical Viva Defense Points:**
  - Dataset: 100% of authentic CIC-IDS2017 (2.83M records across 14 attack classes).
  - Accuracy: 99.78% multi-class Random Forest classifier.
  - Safety boundary: Safe simulation only — zero external exploit packets sent.
  - Zero paid API key dependency: Core system runs entirely on local heuristics and SQLite/PostgreSQL.

---

## 10. Appendix: Architecture & Tech Stack

```text
┌────────────────────────────────────────────────────────┐
│                   REACT 18 FRONTEND                    │
│   TypeScript · Vite · Zustand · Recharts · Leaflet    │
│   Hosted on Vercel: frontend-mauve-chi-80.vercel.app   │
└───────────────────────────┬────────────────────────────┘
                            │ REST / WebSocket
┌───────────────────────────▼────────────────────────────┐
│                  FASTAPI PYTHON BACKEND                │
│       Uvicorn · SQLAlchemy · Pydantic · Scikit-Learn   │
│       Hosted on Render: cybersecurechain-api.onrender  │
├───────────────────────────┬────────────────────────────┤
│  CIC-IDS2017 ML Classifier│  SupplyLens Risk Engine   │
│  80 Features · 99.78% Acc │  Deterministic 0-100 Score │
├───────────────────────────┴────────────────────────────┤
│                    DATA PERSISTENCE                    │
│      SQLite (Local Dev) / PostgreSQL (Production)       │
└────────────────────────────────────────────────────────┘
```

| Layer | Component | Purpose |
|---|---|---|
| **Frontend Framework** | React 18 & TypeScript | Type-safe single page application |
| **Bundler & Tooling** | Vite & Rolldown | High-speed production bundling |
| **State Management** | Zustand | View mode and live alert state |
| **Data Visualization** | Recharts | Posture and risk distribution bar/pie charts |
| **Mapping Engine** | Leaflet & React-Leaflet | Geographic facility and fleet projection |
| **Backend Framework** | FastAPI & Python 3.14 | High-performance asynchronous REST API |
| **Database & ORM** | SQLite & SQLAlchemy | Relational operational and security schema |
| **Intrusion Detection** | Scikit-Learn Random Forest | Real-time traffic classification (CIC-IDS2017) |
| **Threat Intelligence** | OSV.dev & CISA KEV APIs | Live package vulnerability data |
| **SBOM Formats** | CycloneDX 1.4+ & SPDX 2.3 | Open standard software inventory schemas |
| **Frontend Hosting** | Vercel | Production edge CDN deployment |
| **Backend Hosting** | Render Web Services | Cloud Python application runtime |

---

*CyberSecureChain v1.0 — University Project-Based Learning (PBL) & Cybersecurity Portfolio*  
*Academic prototype decision-support tool — safe simulation and deterministic risk modeling.*
