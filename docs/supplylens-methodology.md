# SupplyLens AI: Risk Scoring Methodology & Explainability

## 1. Principles of Explainable Risk Scoring

Traditional cybersecurity tools often rely on opaque machine-learning scores or proprietary "threat intelligence indexes" that cannot be explained or audited during compliance reviews. In contrast, SupplyLens AI adheres to strict explainability principles:

1. **Deterministic:** Given identical input factors, the algorithm always produces the exact same integer risk score and risk band.
2. **Normalized Handling of Incomplete Evidence:** If an asset lacks supplier assessment data or CVSS scores, the engine does *not* treat missing evidence as a score of zero (which would falsely understate risk). Instead, it dynamically renormalizes factor weights over the available evidence set.
3. **Audit Trail Snapshots:** Every computed score can be persisted as a `RiskSnapshot` containing the exact mathematical contributions of each contributing factor.

---

## 2. Multi-Factor Formula

The composite risk score $R \in [0, 100]$ is computed as:

$$R = \text{round}\left( \frac{\sum_{f \in \mathcal{F}_{\text{avail}}} W_f \cdot S_f}{\sum_{f \in \mathcal{F}_{\text{avail}}} W_f} \right)$$

Where:
- $\mathcal{F}_{\text{avail}}$ is the set of factors with verified evidence.
- $W_f$ is the predefined importance weight of factor $f$.
- $S_f \in [0, 100]$ is the normalized factor score.

### Factor Definitions & Weights:

| Factor | Weight ($W_f$) | Evidence Source | Normalization Logic |
| :--- | :--- | :--- | :--- |
| **Vulnerability Severity** | 25% (0.25) | NVD / OSV / CVSS | CVSS score $\times 10$ (e.g. CVSS 9.8 $\rightarrow$ 98.0) or categorical (CRITICAL=100, HIGH=75, MED=50, LOW=25) |
| **Known Exploitation** | 20% (0.20) | CISA KEV Catalog | 100.0 if present in KEV / weaponized; 15.0 if no known active exploit |
| **Business Criticality** | 20% (0.20) | Digital Twin Asset Model | Criticality tier (1–10) $\times 10$ |
| **Dependency Reachability** | 15% (0.15) | SBOM Manifest Scope | Direct dependency: +50; Transitive: +20; Internet-exposed network endpoint: +50 |
| **Supplier Risk** | 10% (0.10) | Vendor Register | Criticality $\times 10$; Assessed vendor: $-25$; Unassessed vendor: $+25$ |
| **Data Sensitivity** | 10% (0.10) | Data Classification Policy | RESTRICTED=100, HIGH=75, MEDIUM=50, LOW=25, PUBLIC=10 |

---

## 3. Qualitative Risk Bands

Final integer scores map directly to qualitative action tiers:

- **CRITICAL (75 – 100):** Immediate exploitation risk or weaponized CVE present in core business service. Mandatory mitigation action required.
- **HIGH (50 – 74):** High-severity vulnerability or critical unvetted tier-1 vendor. Triage within standard sprint cycle.
- **MEDIUM (25 – 49):** Moderate exposure with compensating network segmentation or unweaponized flaw.
- **LOW (0 – 24):** Low-severity finding with negligible operational reachability.
