# SupplyLens AI: End-to-End Demonstration Guide

## Step-by-Step Demonstration Script

This walkthrough illustrates the complete software and supplier risk intelligence workflow for faculty evaluators, viva presentations, and project demos.

---

### Step 1: Ingesting an SBOM Manifest
1. Navigate to **SupplyLens AI** in the left sidebar and select **SBOM Imports** (`/supplylens/sbom-imports`).
2. Select the target software project: `NEXORA Warehouse Management Core (NEX-WMS-CORE)`.
3. Notice the pre-filled CycloneDX 1.4 JSON manifest containing `log4j-core@2.14.1` and `spring-core@5.3.15`.
4. Click **Import SBOM**.
5. Observe the green confirmation alert indicating successful parsing, components added, and dependency graph edge extraction.

---

### Step 2: Component Inventory & Live Threat Enrichment
1. Navigate to **Components** (`/supplylens/components`).
2. Filter by search: `log4j`.
3. Notice `log4j-core` marked as `CRITICAL` risk with known vulnerabilities.
4. Click the **OSV Enrich** button on any component card.
5. Watch the real-time query execute against OSV.dev and update the finding count without reloading the page.
6. Click the component row to open the full inspection drawer displaying raw PURL metadata and license details.

---

### Step 3: Vulnerability Register & CISA KEV Triage
1. Navigate to **Findings** (`/supplylens/findings`).
2. Review the list of CVEs:
   - `CVE-2021-44228` (Log4Shell) tagged with the gold **CISA KEV** badge.
   - `CVE-2022-22965` (Spring4Shell) tagged as Critical RCE.
3. Use the **Status** dropdown on `CVE-2021-44228` to update the triage state from `OPEN` to `IN_TRIAGE`.
4. Click **Export CSV** to download `supplylens-findings.csv` for audit documentation.

---

### Step 4: Tracing Cyber-Physical Exposure
1. Navigate to **Exposure Map** (`/supplylens/exposure-map`).
2. Inspect the multi-stage visual chain:
   $$\text{log4j-core} \longrightarrow \text{WMS-PickPack-Service} \longrightarrow \text{SRV-WMS-01} \longrightarrow \text{FC-DEL-01 (Delhi)}$$
3. Explain to the evaluator: *"This proves that a software vulnerability in an Apache logging package directly exposes the physical picking and sorting robotics at the Delhi Fulfillment Center."*

---

### Step 5: What-If Resilience Scenario Lab
1. Navigate to **Scenario Lab** (`/supplylens/scenario-lab`).
2. Select **Upstream Supplier Package Tampering**.
3. Click **Evaluate Scenario**.
4. Compare the side-by-side impact:
   - **Baseline:** 8 modeled assets compromised, ₹4,250,000 revenue loss, 120 minutes downtime.
   - **Hardened:** Contained at boundary (1 asset reached, ₹0 revenue loss).

---

### Step 6: Asking the AI Risk Copilot
1. Navigate to **AI Copilot** (`/supplylens/ai-copilot`).
2. Click the suggested prompt: *"Explain the operational risk of Log4Shell on fulfillment centers"*.
3. Click **Analyze**.
4. Observe the instant, grounded executive summary citing specific CVEs, mapped facilities, and concrete mitigation recommendations.
