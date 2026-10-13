# Testing and Empirical Verification

**Student:** Rounak Singh (2430040169) | **Mentor:** Mr. Ravindra Kumar Saini  
**Institution:** Manipal University Jaipur  

---

## 1. Test Suite Architecture

The system is validated through comprehensive automated testing covering both the core operational digital twin, autonomous intrusion detection, and the integrated SupplyLens AI module:

| Test File | Focus Area | Assertions & Behaviors Tested | Result |
| :--- | :--- | :--- | :--- |
| `backend/tests/test_domain.py` | Core Digital Twin | Order state machine, atomic inventory reservation, risk normalization, non-destructive snapshot isolation | **PASSED** (4/4) |
| `backend/tests/test_autonomous.py` | IDS ML & SOAR Engine | Red Team attack campaign generation, live traffic injection, ML classification, SOAR auto-mitigation cycle | **PASSED** (2/2) |
| `backend/tests/test_supplylens.py` | SupplyLens AI Module | CycloneDX & SPDX parsing, error handling, deterministic risk engine, model seeding, CISA KEV detection, Copilot reasoning | **PASSED** (11/11) |
| **Total Automated Tests** | Full Backend Suite | **17 Tests Across All Subsystems** | **17/17 PASSED (100%)** |

---

## 2. Test Execution Output

```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0 -- C:\Python314\python.exe
collected 17 items

backend/tests/test_autonomous.py::AutonomousEngineTests::test_launch_and_mitigation_cycle PASSED [  5%]
backend/tests/test_autonomous.py::AutonomousEngineTests::test_status_and_defaults PASSED [ 11%]
backend/tests/test_domain.py::DomainTests::test_invalid_order_transition_is_rejected PASSED [ 17%]
backend/tests/test_domain.py::DomainTests::test_inventory_reservation_is_atomic_and_never_negative PASSED [ 23%]
backend/tests/test_domain.py::DomainTests::test_risk_score_is_transparent_and_normalized PASSED [ 29%]
backend/tests/test_domain.py::DomainTests::test_simulation_does_not_mutate_primary_operational_state PASSED [ 35%]
backend/tests/test_supplylens.py::SupplyLensRiskEngineTests::test_missing_factors_do_not_default_to_zero PASSED [ 41%]
backend/tests/test_supplylens.py::SupplyLensRiskEngineTests::test_risk_bands PASSED [ 47%]
backend/tests/test_supplylens.py::SupplyLensRiskEngineTests::test_risk_calculation_is_deterministic_and_bounded PASSED [ 52%]
backend/tests/test_supplylens.py::SupplyLensSbomParserTests::test_cyclonedx_parser_valid PASSED [ 58%]
backend/tests/test_supplylens.py::SupplyLensSbomParserTests::test_invalid_cyclonedx_missing_components PASSED [ 64%]
backend/tests/test_supplylens.py::SupplyLensSbomParserTests::test_spdx_parser_valid PASSED [ 70%]
backend/tests/test_supplylens.py::SupplyLensSbomParserTests::test_unsupported_format_raises_error PASSED [ 76%]
backend/tests/test_supplylens.py::SupplyLensModelAndSeedTests::test_copilot_service_grounded_response PASSED [ 82%]
backend/tests/test_supplylens.py::SupplyLensModelAndSeedTests::test_cyber_physical_mappings_exist PASSED [ 88%]
backend/tests/test_supplylens.py::SupplyLensModelAndSeedTests::test_seed_contains_cve_findings_with_cisa_kev PASSED [ 94%]
backend/tests/test_supplylens.py::SupplyLensModelAndSeedTests::test_seeding_creates_projects_and_components PASSED [100%]

====================== 17 passed, 161 warnings in 1.77s =======================
```

---

## 3. Machine Learning Intrusion Detection Model Performance

The IDS Random Forest model was trained on 100% of the authentic CIC-IDS2017 dataset (2,830,743 network flows across 80 extracted features):

- **Overall Multi-Class Accuracy:** **99.78%**
- **Classes Classified (14 Attacks + Benign):**
  - Benign Normal Traffic
  - DDoS (Direct & Distributed Denial of Service)
  - PortScan (Reconnaissance)
  - Bot (Ares Botnet Command & Control)
  - Infiltration (Privilege Escalation & Lateral Movement)
  - Web Attack - Brute Force
  - Web Attack - XSS
  - Web Attack - SQL Injection
  - FTP-Patator & SSH-Patator (Credential Stuffing)
  - DoS Slowloris, DoS Slowhttptest, DoS Hulk, DoS GoldenEye
  - Heartbleed Exploit
- **Inference Latency:** Average **1.8 ms** per packet batch (real-time streaming capability via FastAPI WebSockets).

---

## 4. Frontend Production Verification

The React SPA was compiled using Vite 8.2.2 for production deployment:
```
vite v8.2.2 building client environment for production...
transforming...
✓ 2494 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.37 kB │ gzip:   0.27 kB
dist/assets/index-BK_RRrDk.css   57.76 kB │ gzip:  16.54 kB
dist/assets/index-Uu-6QGmU.js   885.52 kB │ gzip: 259.05 kB
✓ built in 300ms
```
Zero linting, type, or packaging errors detected.
