# CyberSecureChain — Complete Step-by-Step User Guide

> **Project:** CyberSecureChain: A Cybersecurity-Driven Supply Chain Digital Twin with AI-Assisted Software and Supplier Risk Intelligence
> **Student:** Rounak Singh (Reg: 2430040169) · B.Tech CSE (Cyber Security) · Manipal University Jaipur
> **Guide:** Mr. Ravindra Kumar Saini
> **Live App:** https://frontend-mauve-chi-80.vercel.app
> **Backend API:** https://cybersecurechain-api.onrender.com

---

## Table of Contents

1. [Getting Started — Opening the App](#1-getting-started)
2. [Operations Mode — Admin View](#2-operations-mode)
3. [Cyber Resilience Mode — Cyber View](#3-cyber-resilience-mode)
4. [SupplyLens AI Mode — Software & Supplier Risk](#4-supplylens-ai-mode)
5. [Live Attack Simulation (Red vs Blue)](#5-live-attack-simulation)
6. [AI Copilot — Risk Queries](#6-ai-copilot)
7. [SBOM Ingestion Walkthrough](#7-sbom-ingestion)
8. [Scenario Lab — Resilience Comparison](#8-scenario-lab)
9. [API & Backend Direct Access](#9-api--backend)
10. [Running Locally](#10-running-locally)
11. [Evaluator Demo Checklist](#11-evaluator-demo-checklist)

---

## 1. Getting Started

### Step 1.1 — Open the Application

Open your browser and navigate to:

```
https://frontend-mauve-chi-80.vercel.app
```

> **First load on Render (free tier):** The backend may take **20–30 seconds** to wake up if it has been idle. Wait for the overview cards to populate — the spinning loader will disappear once data arrives.

### Step 1.2 — Understand the Unified Navigation Modes

### Step 1.2 — Understand the Streamlined Navigation Modes

At the top-left of the sidebar you will see **two balanced mode-switch buttons**:

| Button | Mode | Key Categories |
|---|---|---|
| **ADMIN** | Operations Control Tower | Operational twin — Overview, Facilities, Inventory, Products, Orders, Shipments, Fleet, Employees, Machines, IoT & OT, Digital Twin |
| **CYBER** | Cyber Resilience & SupplyLens AI | Complete defense suite consolidated into **7 high-impact modules**: |

#### The 7 Consolidated CYBER Modules:

1. **⚡ Auto Defense (`/cyber/auto-defense`):** Self-defending twin (Adversary AI vs. CIC-IDS2017 ML Classifier vs. SOAR Order Rerouting).
2. **🛡️ Command Center (`/cyber/command-center`):** Unified executive posture dashboard:
   - *Tab 1:* Enterprise Cyber Posture (Posture score, asset breakdown, risk distribution)
   - *Tab 2:* Software Supply Chain Posture (Projects, SBOM packages, supplier risk, recent CVEs)
   - *Tab 3:* Controls & Resilience (MFA, network segmentation, patch state, readiness score)
   - *Tab 4:* Incident Operations & Audit (Active incidents, response actions, unified timeline)
3. **🔍 Vulnerabilities & Findings (`/cyber/vulnerabilities`):**
   - *Tab 1:* Software & Package CVEs (CVSS score, CISA KEV badges, status triage, CSV export)
   - *Tab 2:* Host & Infrastructure Weaknesses (Cyber asset vulnerabilities, recommended controls)
4. **🗺️ Attack Surface & Exposure (`/cyber/exposure`):**
   - *Tab 1:* Cyber-Physical Exposure Map (Package → Service → Host → Facility → Orders propagation)
   - *Tab 2:* Host Attack Surface & Lateral Paths (Entry points, exposed assets, lateral movement paths)
5. **🧪 Simulation & Scenario Lab (`/cyber/simulation-lab`):**
   - *Tab 1:* Supply Chain Scenario Lab (Vendor bankruptcy, critical CVE exploit, SolarWinds SBOM tampering)
   - *Tab 2:* What-If Facility Resilience (Baseline vs. Hardened resilience comparison, revenue loss)
   - *Tab 3:* Direct Disruption Stress Test (Live attack injection, killchain execution, blast radius)
6. **📦 Software & Supplier Inventory (`/cyber/inventory`):**
   - *Tab 1:* Software Components (SBOM packages, PURL ecosystem inference, live OSV enrichment)
   - *Tab 2:* Supplier Intelligence Register (Vendor risk ratings, assessment status, Add Supplier modal)
   - *Tab 3:* Import SBOM Manifests (CycloneDX / SPDX JSON upload and paste form)
7. **🤖 AI Risk Copilot (`/cyber/ai-copilot`):** Grounded decision support for natural language risk queries with evidence tracing and non-LLM fallback.

### Step 1.3 — Live Event Feed

The **bottom-right live feed** (small panel) shows real-time WebSocket events — adversary attacks, IDS detections, SOAR mitigations, inventory changes, and shipment transitions. It updates automatically without page refresh.

---

## 2. Operations Mode

> **Mode button:** ADMIN | **Default URL:** `/admin/overview`

### Step 2.1 — Overview Dashboard

**URL:** `/admin/overview`

**What you see:**
- **KPI row at top:** Total facilities, active orders, shipments in transit, and overall inventory health — all pulled live from the database.
- **Bar chart:** Orders by status (PENDING, PROCESSING, SHIPPED, DELIVERED).
- **Pie chart:** Inventory distribution across facilities.
- **Live event feed column:** Scrollable recent activity log.
- **Map view:** Leaflet map showing all NEXORA facility locations; click any marker to open the facility detail drawer.

**How to use it:**
1. Click any bar in the bar chart → the chart tooltip shows exact counts.
2. Click any map marker → a **slide-in drawer** appears on the right with facility details (name, type, city, status, capacity).
3. Watch the live event panel — events arrive every few seconds from the simulated supply chain engine.

---

### Step 2.2 — Supply Chain / Digital Twin

**URL:** `/admin/digital-twin` (or click **Supply Chain** in sidebar)

Shows the network graph of how facilities relate to each other — factory → warehouse → distribution centre → customer hub.

---

### Step 2.3 — Facilities

**URL:** `/admin/facilities`

Sortable table of all NEXORA facilities with columns: Facility Code, Type, Location, Status, Capacity.

**How to use:**
1. Click any row → drawer opens showing full facility data.
2. Status badges (OPERATIONAL / DEGRADED / OFFLINE) are colour-coded.

---

### Step 2.4 — Inventory

**URL:** `/admin/inventory`

Table showing every SKU at every facility with **Available**, **Reserved**, and **Quarantined** quantities.

> Quarantined inventory is physically isolated stock flagged by the cyber or operational risk engine.

---

### Step 2.5 — Products, Orders, Shipments

| Page | URL | Key columns |
|---|---|---|
| Products | `/admin/products` | SKU, Name, Category, Supplier, Factory |
| Orders | `/admin/orders` | Order #, Customer, Origin, Destination, Status, **Cyber Status** |
| Shipments | `/admin/shipments` | Shipment Code, Order, Vehicle, Destination, Status, **Integrity** |

**Cyber Status** on Orders and **Integrity** on Shipments are the cyber-physical link — they change when an active attack affects a facility that handles the order.

---

### Step 2.6 — Fleet

**URL:** `/admin/fleet`

Live vehicle positions and status. Vehicles are rerouted automatically during facility attacks (visible in the cyber simulation).

---

### Step 2.7 — Employees, Machines & Robots, IoT & OT

These tables list the human and machine assets of NEXORA.

| Page | Notable columns |
|---|---|
| Employees | MFA status, Account Status |
| Machines & Robots | Zone, Criticality, **Cyber status** |
| IoT & OT | Network segment, **Cyber status** |

The **Cyber status** columns update in real time during attacks.

---

## 3. Cyber Resilience Mode

> **Mode button:** CYBER | **Default URL:** `/cyber/security-overview`

### Step 3.1 — Security Overview

**URL:** `/cyber/security-overview`

**What you see:**
- Security posture score (0–100, higher = better).
- Critical assets count, high-risk assets, active incidents, external connections.
- Donut chart of asset risk distribution.
- Table of highest-risk assets with clickable rows.

---

### Step 3.2 — Auto Defense Center ⚡ (Most Important Feature)

**URL:** `/cyber/auto-defense`

This is the **autonomous Red-vs-Blue AI engine**. It runs automatically every few seconds.

**How to read the screen:**

1. **Adversary AI panel (left):** Shows the current attack campaign — which facility, which attack scenario (Ransomware, OT Disruption, Database Exfiltration), which stage (RECON → ATTACK_IN_PROGRESS → ML_IDS_DETECTED → MITIGATED).
2. **IDS/ML Detector panel (centre):** Shows what the Random Forest ML model (trained on CIC-IDS2017, 99.78% accuracy) detected — traffic features, prediction confidence, classification label.
3. **SOAR Defender panel (right):** Shows defensive actions taken — isolation, rerouting orders, patching, alert broadcast.

**Observing an attack cycle:**
1. Wait a few seconds — the adversary AI will launch a campaign automatically.
2. Watch the attack stage progress: RECON → ATTACK_IN_PROGRESS.
3. The IDS detects it: stage changes to ML_IDS_DETECTED.
4. SOAR auto-mitigates: stage changes to MITIGATED.
5. The attack overlay on the Admin screen also clears.

**Manual injection:**
- The **Admin Overview** page has a "Simulate Attack" panel — pick a facility and click **Inject** to manually start an attack and watch the full cycle in real time.

---

### Step 3.3 — Simulation

**URL:** `/cyber/simulation`

Run controlled facility disruption simulations without affecting the primary operational state.

**Steps:**
1. Select a facility from the dropdown.
2. Choose a disruption type (e.g., COMPLETE_SHUTDOWN, RANSOMWARE_ATTACK).
3. Click **Run Simulation**.
4. View the projected impact on orders, inventory, and revenue in the comparison table.

---

### Step 3.4 — Attack Surface

**URL:** `/cyber/attack-surface`

Lists every exposed cyber asset — servers, OT controllers, IoT gateways — with their surface type, facility, and risk level.

---

### Step 3.5 — Vulnerabilities

**URL:** `/cyber/vulnerabilities`

Lists known vulnerabilities across cyber assets. Each row shows: Vulnerability ID, Affected Asset, Facility, Severity, and Recommended Control.

---

### Step 3.6 — Incidents

**URL:** `/cyber/incidents`

Log of all security incidents — past and ongoing. Includes incident type, affected facility, status, and timeline.

---

### Step 3.7 — Attack Paths

**URL:** `/cyber/attack-paths`

Maps how an attacker could pivot from a compromised asset through the network using known vulnerabilities.

---

### Step 3.8 — Risk Register

**URL:** `/cyber/risk`

Every cyber asset ranked by risk score (0–100) with a "Contributing factors" column explaining the transparent scoring logic.

---

### Step 3.9 — Controls

**URL:** `/cyber/controls`

Security controls currently applied across the digital twin (MFA enforcement, network segmentation, encryption, patch status).

---

### Step 3.10 — What-If Resilience Comparison

**URL:** `/cyber/what-if`

Side-by-side comparison of **baseline state** vs. **hardened state** for a selected facility.

**Steps:**
1. Select a facility.
2. Click **Run What-If**.
3. Compare projected order disruptions, revenue loss, and recovery time between baseline and hardened.

---

### Step 3.11 — Timeline / Unified Events

**URL:** `/cyber/timeline`

Chronological log of every event in the digital twin — operational changes, cyber events, IDS alerts, SOAR responses, and SupplyLens findings.

---

## 4. SupplyLens AI Mode

> **Mode button:** SUPPLY LENS | **Default URL:** `/supplylens/sl-overview`

### Step 4.1 — SupplyLens Overview

**URL:** `/supplylens/sl-overview`

**What you see:**
- **KPI cards (top row):**
  - Software Projects tracked
  - Total Components (open-source packages)
  - Registered Suppliers
  - Total CVE Findings
  - Open Findings requiring action
  - CISA KEV (Known Exploited Vulnerabilities) count
  - Cyber-physical mappings (package → facility links)
  - Active mitigations
  - Average component risk score
- **Recent Findings panel:** Latest 5 CVEs across all projects with severity badges.

All numbers are live from the database — not hardcoded.

---

### Step 4.2 — SBOM Imports

**URL:** `/supplylens/sbom-imports`

Import a Software Bill of Materials document to register all open-source dependencies of a software project.

**Steps:**
1. **Select project** from the dropdown (or you'll see existing projects like `NEXORA-WMS`, `NEXORA-OT-CONTROLLER`, `NEXORA-API-GATEWAY`).
2. **Choose format:** CycloneDX 1.4+ JSON or SPDX 2.3 JSON.
3. **Upload a file** (drag-and-drop or click to browse) OR **paste raw JSON** into the text area.
4. Click **Import SBOM**.
5. The backend parses: detects format, extracts components with PURL (Package URL), infers ecosystem (npm, pypi, maven, etc.), and maps dependency relationships.
6. A result card appears showing: format detected, components added, dependency relationships mapped, and any parse warnings.

**Example CycloneDX snippet to test with (paste into text area):**
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

---

### Step 4.3 — Components & Dependency Graph

**URL:** `/supplylens/components`

**What you see:**
Full inventory of all software components (open-source packages) imported from SBOMs, with columns:
- Name & Version
- Ecosystem (pypi, npm, maven, etc.)
- PURL (Package URL identifier)
- Direct or Transitive dependency flag
- Risk Score (0–100)
- Risk Level badge (CRITICAL / HIGH / MEDIUM / LOW)
- Finding Count (linked CVEs)
- Supplier (if assigned)
- Deployment Count (cyber-physical links)

**How to use:**
1. **Search** by name using the search box (top right of table).
2. **Filter by severity** using the severity dropdown — shows only components with findings of that severity.
3. Click any row → **drawer opens** with:
   - Full component metadata
   - All linked CVE findings with CVSS scores
   - Cyber-physical deployment mappings
4. Click **OSV Enrich** button on any component row → live query to OSV.dev API fetches the latest known vulnerabilities for that package version and stores them as new findings.

---

### Step 4.4 — Vulnerability Findings

**URL:** `/supplylens/findings`

**What you see:**
All CVE findings across all projects, with columns:
- Vulnerability ID (e.g., CVE-2021-44228 = Log4Shell)
- Component Name
- Severity (CRITICAL / HIGH / MEDIUM / LOW) — colour-coded badge + text label
- CVSS Score (numerical)
- **CISA KEV badge** — red "KEV" badge if this CVE is on the CISA Known Exploited Vulnerabilities catalogue
- Status (OPEN / IN_TRIAGE / MITIGATED / ACCEPTED)
- Fixed Version (what version resolves the CVE)
- Risk Score
- Source (OSV / SEED / LIVE_OSV)

**How to use:**
1. **Filter by severity** — select CRITICAL to see only the most dangerous findings.
2. **Filter by status** — select OPEN to see unresolved findings.
3. Click any row → **drawer** shows full finding detail including CVE description, affected versions, CVSS breakdown, and linked mitigations.
4. **Change status** on any finding → click the status dropdown in the row and select IN_TRIAGE, MITIGATED, or ACCEPTED. The change saves immediately to the database.
5. **Export CSV** → click the **Download CSV** button (top right) to export all visible findings as a `.csv` file for reporting.

**Pre-loaded demo findings (real CVEs with synthetic demo data):**

| CVE | Package | Severity | CISA KEV |
|---|---|---|---|
| CVE-2021-44228 | log4j-core 2.14.1 | CRITICAL | ✅ Yes (Log4Shell) |
| CVE-2022-22965 | spring-webmvc 5.3.17 | CRITICAL | ✅ Yes (Spring4Shell) |
| CVE-2020-14343 | PyYAML 5.3.1 | HIGH | No |
| CVE-2022-42889 | commons-text 1.9 | HIGH | No (Text4Shell) |
| CVE-2021-34434 | eclipse-mosquitto 2.0.11 | MEDIUM | No |

---

### Step 4.5 — Supplier Intelligence

**URL:** `/supplylens/suppliers`

**What you see:**
Vendor/supplier register with risk assessment status, columns:
- Supplier Code & Name
- Category (SOFTWARE / HARDWARE / LOGISTICS / CLOUD)
- Tier (TIER_1 / TIER_2 / TIER_3)
- Criticality score (1–10)
- Assessment Status (ASSESSED / PENDING_REVIEW / UNDER_REVIEW)
- Risk Score & Risk Level
- Data Sensitivity (HIGH / MEDIUM / LOW)
- Component Count (how many software components they supply)

**How to use:**
1. Click any supplier row → **drawer** shows full detail including contact, evidence URL, notes, and all linked components.
2. Click **Add Supplier** button (top right) → opens a registration modal with fields: Code, Name, Category, Tier, Criticality, Contact Email, Data Sensitivity, Assessment Status, Notes.
3. Fill in the form and click **Create Supplier** — new supplier appears in the table instantly.
4. Suppliers in **PENDING_REVIEW** status carry higher risk scores in the risk engine.

**Pre-loaded demo suppliers:**

| Supplier | Category | Tier | Assessment |
|---|---|---|---|
| Apache Software Foundation | SOFTWARE | TIER_1 | ASSESSED |
| Eclipse Foundation | SOFTWARE | TIER_2 | ASSESSED |
| Spring.io (VMware) | SOFTWARE | TIER_1 | UNDER_REVIEW |
| Python Software Foundation | SOFTWARE | TIER_1 | ASSESSED |
| Unnamed Cloud CDN | CLOUD | TIER_3 | PENDING_REVIEW |

---

### Step 4.6 — Software-to-Operations Exposure Map

**URL:** `/supplylens/exposure-map`

**What it shows:**
This is the defining feature of SupplyLens AI — the **cyber-physical propagation chain**:

```
Package (CVE) → Service → Host (Cyber Asset) → Facility → Orders / Operations
```

**KPI row:**
- Total mappings, facilities exposed, verified mappings vs user-mapped

**Table columns:**
- Component (vulnerable package)
- Service Name (e.g., "WMS Order Processing Service")
- Business Process (e.g., "Fulfillment Operations")
- Mapping Type (VERIFIED / INFERRED / USER_MAPPED)
- Facility (which physical facility is at risk)
- Cyber Asset (the host/server running the software)

**How to use:**
1. Read each row as: *"[Package] is deployed in [Service] at [Facility], affecting [Business Process]"*
2. Click any row → **drawer** opens showing:
   - The package with its full CVE findings
   - The cyber asset hosting it (with risk level)
   - The facility it belongs to (with operational status)
   - The orders that flow through that facility
3. Click **Delete mapping** (trash icon) on any row to remove a user-created mapping.
4. To **add a new mapping**: use the **Create Deployment** button and fill in component, service name, facility, and cyber asset.

---

## 5. Live Attack Simulation

### Step 5.1 — Watch the Autonomous Cycle (Automatic)

1. Go to **CYBER → Auto Defense** (`/cyber/auto-defense`).
2. The system runs a full Red-vs-Blue cycle automatically every ~15–30 seconds.
3. Watch the stage badges: `RECON` → `ATTACK_IN_PROGRESS` → `ML_IDS_DETECTED` → `MITIGATED`.

### Step 5.2 — Manually Inject an Attack

1. Go to **ADMIN → Overview** (`/admin/overview`).
2. Scroll down to the **"Simulate Live Attack"** panel.
3. Select a **Facility** from the dropdown (e.g., WH-MUMBAI-01).
4. Click **Inject Attack**.
5. Switch to **ADMIN** view — the entire app shell turns red/orange with the attack overlay (facility-specific message: ransomware / DDoS / SQL injection depending on the attack scenario).
6. Watch the **damage counter** in the overlay increment in real-time (₹ per second).
7. Switch to **CYBER → Auto Defense** — watch the IDS detect it.
8. SOAR auto-mitigates within ~10 seconds — the overlay disappears.
9. Check **ADMIN → Orders** — affected orders will show `cyber_status: DISRUPTED` then recover.

### Step 5.3 — What-If Comparison

1. Go to **CYBER → What-If** (`/cyber/what-if`).
2. Select any facility.
3. Click **Run What-If Analysis**.
4. Compare the two-column table: **Baseline** (no mitigations) vs **Hardened** (all controls applied).
5. Metrics compared: projected orders disrupted, revenue at risk, recovery time hours.

---

## 6. AI Copilot

**URL:** `/supplylens/ai-copilot`

The AI Risk Copilot answers **grounded risk queries** using only the evidence stored in the database — no external LLM calls, no hallucination.

### Step 6.1 — Ask a Risk Question

1. Navigate to **SUPPLY LENS → AI Copilot**.
2. Type a question in the prompt box, for example:
   - `"What are the most critical CVEs in the system?"`
   - `"Which suppliers have the highest risk score?"`
   - `"How many CISA KEV findings are unmitigated?"`
   - `"Which components are deployed at high-criticality facilities?"`
   - `"Explain the exposure chain for Log4Shell"`
3. Click **Ask Copilot**.
4. The response panel shows:
   - **Answer** — structured text grounded in database state
   - **Evidence** — the actual data records used to form the answer
   - **Methodology** — how the answer was derived (deterministic, not LLM-invented)
   - **Confidence** — based on evidence completeness

### Step 6.2 — Project-Scoped Queries

- Use the **Project** dropdown to scope the query to a specific software project (e.g., NEXORA-WMS only).
- Click **Clear** to reset and ask a new question.

> **Important academic note:** The copilot explicitly labels synthetic demo data and will not claim external scan results or confirmed exploitation. The system is designed for decision-support, not as a production security guarantee.

---

## 7. SBOM Ingestion

*(Full walkthrough — for demo or evaluation)*

### Step 7.1 — Navigate to SBOM Imports

Click **SUPPLY LENS → SBOM Imports** in the sidebar.

### Step 7.2 — Select or Create a Project

- Use the **Project** dropdown to select an existing project (e.g., NEXORA-WMS).
- Or click **New Project** to create one:
  - Fill in: Code (e.g., `MY-APP`), Name, Description, Version, Business Owner, Criticality (1–10).
  - Optionally link to a Facility.
  - Click **Create Project**.

### Step 7.3 — Choose SBOM Format

Toggle between:
- **CycloneDX 1.4+ JSON** (recommended — widely supported by tools like cdxgen, Syft, Trivy)
- **SPDX 2.3 JSON** (NTIA standard format)

### Step 7.4 — Provide the SBOM

**Option A — Upload file:**
- Drag a `.json` file onto the upload zone, or click to browse.

**Option B — Paste JSON:**
- Click the **Paste JSON** tab.
- Paste raw SBOM content into the text area.
- Use the sample CycloneDX snippet from Section 4.2 for a quick test.

### Step 7.5 — Import

Click **Import SBOM**. The backend:
1. Validates the JSON format (CycloneDX or SPDX detection).
2. Extracts each component: name, version, PURL, license, direct/transitive flag.
3. Maps dependency relationships.
4. Stores everything in the database under the selected project.
5. Returns: components added, relationships mapped, warnings (if any).

### Step 7.6 — View Imported Components

Go to **SUPPLY LENS → Components** — your newly imported packages appear in the table.

### Step 7.7 — Enrich with Live CVE Data

On any component row, click **OSV Enrich** to query OSV.dev and retrieve known vulnerabilities. New findings appear in **SUPPLY LENS → Findings**.

---

## 8. Scenario Lab — Resilience Comparison

**URL:** `/supplylens/scenario-lab`

### Step 8.1 — Configure Scenario

1. Navigate to **SUPPLY LENS → Scenario Lab**.
2. Select a **Software Project** (e.g., NEXORA-WMS — the warehouse management system).
3. Select a **Disruption Type:**
   - `VENDOR_BANKRUPTCY` — primary software supplier goes offline
   - `CRITICAL_CVE_EXPLOIT` — a CRITICAL CVE is actively exploited
   - `SBOM_SUPPLY_CHAIN_ATTACK` — upstream package tampered (SolarWinds-style)
   - `MASS_PATCHING_DOWNTIME` — emergency patching requires planned downtime

### Step 8.2 — Run Analysis

Click **Run Scenario Analysis**.

### Step 8.3 — Read the Results

The side-by-side comparison shows:

| Metric | Baseline (Unmitigated) | Hardened (Mitigated) |
|---|---|---|
| Orders at risk | High | Reduced |
| Revenue exposure | High | Reduced |
| Recovery time | Days | Hours |
| Mean time to detect | High | Low |
| Patch coverage | Low | High |

**Recommended controls** are listed for the hardened state — what specific mitigations reduce risk.

---

## 9. API & Backend Direct Access

The FastAPI backend exposes interactive documentation at:

```
https://cybersecurechain-api.onrender.com/docs
```

### Key API endpoints to explore:

| Endpoint | Description |
|---|---|
| `GET /api/digital-twin` | Full digital twin snapshot |
| `GET /api/facilities` | All NEXORA facilities |
| `GET /api/orders` | All orders with cyber status |
| `GET /api/cyber/risk` | Risk scores for all cyber assets |
| `GET /api/supplylens/overview` | SupplyLens KPI summary |
| `GET /api/supplylens/components` | All software components |
| `GET /api/supplylens/findings` | All CVE findings |
| `GET /api/supplylens/suppliers` | Supplier register |
| `GET /api/supplylens/deployments` | Cyber-physical exposure mappings |
| `POST /api/supplylens/projects/{id}/import-sbom` | Import an SBOM |
| `POST /api/supplylens/copilot/query` | AI Copilot query |
| `GET /api/supplylens/reports/findings.csv` | Export findings as CSV |
| `GET /api/cyber/simulate/{facility}` | Run cyber simulation |

---

## 10. Running Locally

### Prerequisites

- Python 3.11+ (`C:\Python314\python.exe` or equivalent)
- Node.js 20+ (or use the bundled runtime)

### Step 10.1 — Clone the Repository

```bash
git clone https://github.com/rounaksinghsingh2004-hub/cybersecurechain.git
cd cybersecurechain
```

### Step 10.2 — Start the Backend (FastAPI)

```powershell
# From project root
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend runs at: `http://127.0.0.1:8000`
API docs at: `http://127.0.0.1:8000/docs`

> The database (`cybersecurechain.db`) is created automatically on first run with all seed data — operational twin + SupplyLens demo records.

### Step 10.3 — Start the Frontend (Vite)

```powershell
# In a new terminal, from project root
cd frontend
npm install   # or: pnpm install
npm run dev   # or: pnpm dev
```

Frontend runs at: `http://localhost:5173`

### Step 10.4 — Run Tests

```powershell
# From project root
$env:PYTHONPATH = "backend"
python -m pytest backend/tests -v
# Expected: 17/17 PASSED
```

---

## 11. Evaluator Demo Checklist

Use this checklist during a live faculty evaluation or viva:

### Operations Digital Twin
- [ ] Open `/admin/overview` — show live KPI cards (not hardcoded)
- [ ] Click a map marker — show facility drawer
- [ ] Open `/admin/orders` — show cyber_status column
- [ ] Open `/admin/shipments` — show integrity column

### Cyber Resilience
- [ ] Open `/cyber/security-overview` — show posture score and risk chart
- [ ] Open `/cyber/auto-defense` — wait for autonomous attack cycle
- [ ] Inject a manual attack from `/admin/overview` — show attack overlay
- [ ] Watch SOAR mitigate it — overlay clears
- [ ] Open `/cyber/what-if` — run baseline vs hardened comparison
- [ ] Open `/cyber/risk` — show transparent risk scoring with "Contributing factors"

### SupplyLens AI
- [ ] Open `/supplylens/sl-overview` — show all KPIs loaded from database
- [ ] Open `/supplylens/findings` — show CVEs with CISA KEV badges
- [ ] Change a finding status (e.g., OPEN → IN_TRIAGE) — show it saves
- [ ] Export CSV — download findings.csv
- [ ] Open `/supplylens/sbom-imports` — paste sample CycloneDX JSON and import
- [ ] Navigate to `/supplylens/components` — show newly added package
- [ ] Click OSV Enrich on a component — show live vulnerability fetch
- [ ] Open `/supplylens/exposure-map` — trace Log4Shell → WMS → WH-MUMBAI → Orders
- [ ] Open `/supplylens/ai-copilot` — ask "Which CISA KEV findings are open?"
- [ ] Open `/supplylens/scenario-lab` — run CRITICAL_CVE_EXPLOIT scenario

### API & Docs
- [ ] Open `https://cybersecurechain-api.onrender.com/docs` — show live Swagger UI
- [ ] Call `GET /api/supplylens/overview` directly — show JSON response
- [ ] Explain the transparent risk scoring formula (6-factor weighted sum, 0–100 output)

### Academic Boundaries (explain clearly in viva)
- [ ] All data is synthetic demo data for NEXORA (fictional company)
- [ ] No external infrastructure is scanned or attacked
- [ ] The ML model is a Random Forest trained on CIC-IDS2017 (real public dataset)
- [ ] The AI Copilot is deterministic — it reads the database, not an LLM
- [ ] Risk scores are explainable — each factor is shown separately

---

## Appendix: Key Technologies Used

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | React 18, TypeScript, Vite | UI framework and build |
| State management | Zustand | Global view/mode state |
| Charts | Recharts | Bar, pie, area charts |
| Maps | Leaflet / React-Leaflet | Facility location maps |
| Icons | Lucide React | Consistent icon set |
| Backend | FastAPI, Python 3.14 | REST API and WebSocket |
| ORM | SQLAlchemy | Database models |
| Database | SQLite (local) / PostgreSQL (prod) | Persistent data store |
| ML Model | scikit-learn Random Forest | IDS traffic classification |
| Dataset | CIC-IDS2017 | 2.83M rows, 14 attack classes |
| Threat Intel | OSV.dev, CISA KEV | Live CVE data (on demand) |
| SBOM formats | CycloneDX 1.4+, SPDX 2.3 | Software bill of materials |
| Hosting (FE) | Vercel | React production deployment |
| Hosting (BE) | Render | FastAPI production deployment |
| Source Control | GitHub | Version control and CI |

---

*Document generated: October 14, 2026 — CyberSecureChain v1.0 (SupplyLens AI integrated)*
*Academic project — research/prototype decision-support tool, not a production security guarantee.*
