"""
SupplyLens AI module tests for CyberSecureChain.
Verifies:
- Deterministic explainable risk engine
- CycloneDX JSON parser
- SPDX JSON parser
- Malformed & invalid SBOM validation
- SupplyLens database models & seeding
- Cyber-physical mapping resolution
- Deterministic Risk Copilot service
"""
import unittest
import asyncio
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models import (
    Base,
    Supplier,
    SoftwareProject,
    SoftwareComponent,
    ComponentFinding,
    ComponentDeployment,
    MitigationAction,
)
from app.services.supplylens_risk import calculate_risk, get_risk_band
from app.services.supplylens_sbom import (
    detect_sbom_format,
    parse_cyclonedx_json,
    parse_spdx_json,
    SbomValidationError,
)
from app.services.supplylens_copilot import RiskCopilotService
from app.seed_supplylens import seed_supplylens


def create_test_session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class SupplyLensRiskEngineTests(unittest.TestCase):
    def test_risk_calculation_is_deterministic_and_bounded(self):
        factors = {
            "vulnerability_severity": 0.8,
            "known_exploitation": 1.0,
            "business_criticality": 0.7,
            "dependency_exposure": 0.6,
        }
        score1, band1, breakdown1 = calculate_risk(factors)
        score2, band2, breakdown2 = calculate_risk(factors)
        self.assertEqual(score1, score2)
        self.assertEqual(band1, band2)
        self.assertTrue(0 <= score1 <= 100)
        self.assertIn(band1, ("LOW", "MEDIUM", "HIGH", "CRITICAL"))
        self.assertIn("vulnerability_severity", breakdown1)

    def test_missing_factors_do_not_default_to_zero(self):
        factors_full = {
            "vulnerability_severity": 1.0,
            "known_exploitation": 1.0,
            "business_criticality": 1.0,
            "dependency_exposure": 1.0,
            "supplier_risk": 1.0,
            "data_sensitivity": 1.0,
        }
        score_full, band_full, _ = calculate_risk(factors_full)
        self.assertEqual(score_full, 100)
        self.assertEqual(band_full, "CRITICAL")

        # Normalized denominator: partial maxed-out factors still yield 100
        factors_partial = {
            "vulnerability_severity": 1.0,
            "known_exploitation": 1.0,
        }
        score_partial, _, _ = calculate_risk(factors_partial)
        self.assertEqual(score_partial, 100)

    def test_risk_bands(self):
        self.assertEqual(get_risk_band(85), "CRITICAL")
        self.assertEqual(get_risk_band(65), "HIGH")
        self.assertEqual(get_risk_band(45), "MEDIUM")
        self.assertEqual(get_risk_band(15), "LOW")


class SupplyLensSbomParserTests(unittest.TestCase):
    def test_cyclonedx_parser_valid(self):
        cdx = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "components": [
                {
                    "type": "library",
                    "name": "log4j-core",
                    "version": "2.14.1",
                    "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
                    "licenses": [{"license": {"id": "Apache-2.0"}}],
                }
            ],
            "dependencies": [],
        }
        self.assertEqual(detect_sbom_format(cdx), "CYCLONEDX_JSON")
        comps, deps, warnings = parse_cyclonedx_json(cdx)
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]["name"], "log4j-core")
        self.assertEqual(comps[0]["version"], "2.14.1")
        self.assertEqual(comps[0]["ecosystem"], "maven")

    def test_spdx_parser_valid(self):
        spdx = {
            "spdxVersion": "SPDX-2.3",
            "SPDXID": "SPDXRef-DOCUMENT",
            "packages": [
                {
                    "SPDXID": "SPDXRef-Package-spring",
                    "name": "spring-core",
                    "versionInfo": "5.3.15",
                    "licenseConcluded": "Apache-2.0",
                }
            ],
            "relationships": [],
        }
        self.assertEqual(detect_sbom_format(spdx), "SPDX_JSON")
        comps, deps, warnings = parse_spdx_json(spdx)
        self.assertEqual(len(comps), 1)
        self.assertEqual(comps[0]["name"], "spring-core")
        self.assertEqual(comps[0]["version"], "5.3.15")

    def test_unsupported_format_raises_error(self):
        with self.assertRaises(SbomValidationError):
            detect_sbom_format({"unknown_key": "data"})

    def test_invalid_cyclonedx_missing_components(self):
        with self.assertRaises(SbomValidationError):
            parse_cyclonedx_json({"bomFormat": "CycloneDX", "specVersion": "1.4"})


class SupplyLensModelAndSeedTests(unittest.TestCase):
    def setUp(self):
        self.db = create_test_session()
        seed_supplylens(self.db)

    def tearDown(self):
        self.db.close()

    def test_seeding_creates_projects_and_components(self):
        projects = self.db.scalars(select(SoftwareProject)).all()
        self.assertGreaterEqual(len(projects), 1)

        components = self.db.scalars(select(SoftwareComponent)).all()
        self.assertGreaterEqual(len(components), 5)

        suppliers = self.db.scalars(select(Supplier)).all()
        self.assertGreaterEqual(len(suppliers), 3)

    def test_seed_contains_cve_findings_with_cisa_kev(self):
        findings = self.db.scalars(select(ComponentFinding)).all()
        self.assertGreaterEqual(len(findings), 3)

        kev_matches = [f for f in findings if f.cisa_kev]
        self.assertGreaterEqual(len(kev_matches), 1)
        # Verify Log4Shell or Spring4Shell is in the seeded CVEs
        cve_ids = [f.vulnerability_id for f in findings]
        self.assertTrue(any("CVE-2021-44228" in cve for cve in cve_ids))

    def test_cyber_physical_mappings_exist(self):
        deployments = self.db.scalars(select(ComponentDeployment)).all()
        self.assertGreaterEqual(len(deployments), 1)
        first = deployments[0]
        self.assertIsNotNone(first.component_id)
        self.assertIsNotNone(first.service_name)

    def test_copilot_service_grounded_response(self):
        copilot = RiskCopilotService(self.db)
        res = asyncio.run(copilot.query("Explain Log4Shell risk"))
        self.assertIn("summary", res)
        self.assertIn("key_risks", res)
        self.assertIn("confidence_level", res)
