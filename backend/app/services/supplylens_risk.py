"""
SupplyLens AI — Deterministic, Explainable Risk Engine.

Scoring Formula:
Factors:
1. Vulnerability Severity (25% weight): Normalized from CVSS (0-10 -> 0-100) or severity categorical (LOW=25, MED=50, HIGH=75, CRIT=100)
2. Known-Exploitation / CISA KEV (20% weight): 100 if present in KEV or actively weaponized, 0 if confirmed not exploited
3. Business Criticality (20% weight): Normalized from Asset/Project criticality (1-10 -> 10-100)
4. Dependency Reachability & Exposure (15% weight): Direct runtime vs transitive, internet-exposed endpoints
5. Supplier Risk (10% weight): Assessment status, supplier tier, supplier criticality
6. Data Sensitivity & Access (10% weight): Classification of data processed (RESTRICTED=100, HIGH=75, MEDIUM=50, LOW=25)

Deterministic Normalization:
  riskScore = round( sum(weight_i * factor_i) / sum(weights_of_available_factors) )

Risk Bands:
  0 – 24  : LOW
  25 – 49 : MEDIUM
  50 – 74 : HIGH
  75 – 100: CRITICAL
"""
from typing import Any, Dict, List, Optional, Tuple


FACTOR_WEIGHTS = {
    "vulnerability_severity": 0.25,
    "known_exploitation": 0.20,
    "business_criticality": 0.20,
    "dependency_exposure": 0.15,
    "supplier_risk": 0.10,
    "data_sensitivity": 0.10,
}

METHODOLOGY_VERSION = "v1.0-explainable-weights"


class RiskResult(dict):
    """Dictionary that can also be unpacked as (risk_score, risk_level, breakdown)."""
    def __iter__(self):
        yield self["risk_score"]
        yield self["risk_level"]
        yield self["breakdown"]


def get_risk_band(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


def calculate_risk(
    factors_or_cvss: Any = None,
    severity: Optional[str] = None,
    is_cisa_kev: Optional[bool] = None,
    business_criticality: Optional[int] = None,  # 1-10
    is_direct_dependency: Optional[bool] = None,
    is_network_exposed: Optional[bool] = None,
    supplier_criticality: Optional[int] = None,  # 1-10
    supplier_assessed: Optional[bool] = None,
    data_sensitivity: Optional[str] = None,       # LOW, MEDIUM, HIGH, RESTRICTED
    **kwargs,
) -> RiskResult:
    """
    Computes an explainable risk score using only available evidence.
    Accepts either:
    1. A dictionary of normalized factor values (0.0 to 1.0 or 0 to 100)
    2. Explicit keyword arguments (cvss_score, severity, is_cisa_kev, etc.)
    """
    factor_scores: Dict[str, float] = {}
    missing_factors: List[str] = []

    # If first arg is a dictionary of factors
    if isinstance(factors_or_cvss, dict):
        for k, v in factors_or_cvss.items():
            if v is not None and k in FACTOR_WEIGHTS:
                val = float(v)
                if val <= 1.0:
                    val = val * 100.0
                factor_scores[k] = min(100.0, max(0.0, val))
        for k in FACTOR_WEIGHTS:
            if k not in factor_scores:
                missing_factors.append(k)
    else:
        cvss_score = factors_or_cvss
        # 1. Vulnerability Severity
        if cvss_score is not None and 0.0 <= float(cvss_score) <= 10.0:
            factor_scores["vulnerability_severity"] = min(100.0, float(cvss_score) * 10.0)
        elif severity:
            sev_map = {"CRITICAL": 100.0, "HIGH": 75.0, "MEDIUM": 50.0, "LOW": 25.0}
            factor_scores["vulnerability_severity"] = sev_map.get(severity.upper(), 50.0)
        else:
            missing_factors.append("vulnerability_severity")

        # 2. Known Exploitation (CISA KEV)
        if is_cisa_kev is not None:
            factor_scores["known_exploitation"] = 100.0 if is_cisa_kev else 15.0
        else:
            missing_factors.append("known_exploitation")

        # 3. Business Criticality
        if business_criticality is not None and 1 <= business_criticality <= 10:
            factor_scores["business_criticality"] = float(business_criticality * 10)
        else:
            missing_factors.append("business_criticality")

        # 4. Dependency Reachability & Exposure
        if is_direct_dependency is not None or is_network_exposed is not None:
            reachability = 0.0
            if is_direct_dependency is True:
                reachability += 50.0
            elif is_direct_dependency is False:
                reachability += 20.0
            else:
                reachability += 35.0

            if is_network_exposed is True:
                reachability += 50.0
            elif is_network_exposed is False:
                reachability += 10.0
            else:
                reachability += 25.0
            factor_scores["dependency_exposure"] = min(100.0, reachability)
        else:
            missing_factors.append("dependency_exposure")

        # 5. Supplier Risk
        if supplier_criticality is not None or supplier_assessed is not None:
            sup_score = 50.0
            if supplier_criticality is not None:
                sup_score = float(supplier_criticality * 10)
            if supplier_assessed is True:
                sup_score = max(10.0, sup_score - 25.0)
            elif supplier_assessed is False:
                sup_score = min(100.0, sup_score + 25.0)
            factor_scores["supplier_risk"] = min(100.0, sup_score)
        else:
            missing_factors.append("supplier_risk")

        # 6. Data Sensitivity
        if data_sensitivity:
            sens_map = {
                "RESTRICTED": 100.0,
                "HIGH": 75.0,
                "MEDIUM": 50.0,
                "LOW": 25.0,
                "PUBLIC": 10.0,
            }
            factor_scores["data_sensitivity"] = sens_map.get(data_sensitivity.upper(), 50.0)
        else:
            missing_factors.append("data_sensitivity")

    available_factors = list(factor_scores.keys())

    # Fallback if zero evidence available
    if not available_factors:
        return RiskResult({
            "risk_score": 25,
            "risk_level": "MEDIUM",
            "breakdown": {},
            "available_factors": [],
            "missing_factors": list(FACTOR_WEIGHTS.keys()),
            "evidence_coverage_pct": 0.0,
            "methodology_version": METHODOLOGY_VERSION,
            "rationale": "No verified risk factors available; baseline conservative estimate.",
        })

    # Deterministic weighted calculation over available weights
    sum_weights = sum(FACTOR_WEIGHTS[f] for f in available_factors)
    weighted_sum = sum(factor_scores[f] * FACTOR_WEIGHTS[f] for f in available_factors)
    raw_score = weighted_sum / sum_weights
    final_score = int(round(raw_score))
    final_score = max(0, min(100, final_score))

    risk_level = get_risk_band(final_score)

    breakdown = {}
    for f in available_factors:
        normalized_weight = FACTOR_WEIGHTS[f] / sum_weights
        contribution = factor_scores[f] * normalized_weight
        breakdown[f] = {
            "factor_score": round(factor_scores[f], 1),
            "assigned_weight": FACTOR_WEIGHTS[f],
            "normalized_weight": round(normalized_weight, 3),
            "contribution": round(contribution, 1),
        }

    coverage_pct = round((len(available_factors) / len(FACTOR_WEIGHTS)) * 100.0, 1)
    top_driver = max(available_factors, key=lambda f: factor_scores[f])
    rationale = f"Primary risk driver is {top_driver.replace('_', ' ')} (score: {round(factor_scores[top_driver], 1)}/100) based on verified evidence."

    return RiskResult({
        "risk_score": final_score,
        "risk_level": risk_level,
        "breakdown": breakdown,
        "available_factors": available_factors,
        "missing_factors": missing_factors,
        "evidence_coverage_pct": coverage_pct,
        "methodology_version": METHODOLOGY_VERSION,
        "rationale": rationale,
    })
