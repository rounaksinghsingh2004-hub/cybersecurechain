"""
SupplyLens AI — Synthetic Seed Data Generator.

Generates realistic software supply-chain data for NEXORA Commerce & Logistics:
- Tier-1 Suppliers with assessment posture
- Software projects (WMS, Fleet Telematics, OT Robotics Firmware)
- Detailed component trees (direct and transitive) with PURLs and licenses
- Real CVE findings from OSV / CISA KEV
- Cyber-physical deployment mappings linking components to facilities and assets
- Mitigation actions and risk snapshots
"""
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Supplier, SoftwareProject, SbomImportJob, SoftwareComponent,
    ComponentDependency, ComponentFinding, ComponentDeployment,
    MitigationAction, RiskSnapshot, CyberAsset, Facility
)


def seed_supplylens(db: Session) -> None:
    # Check if already seeded
    if db.scalar(select(SoftwareProject.id).limit(1)):
        return

    # 1. Facilities lookup
    facilities_by_code = {f.code: f for f in db.scalars(select(Facility)).all()}
    fc_jpr = facilities_by_code.get("FC-JPR-01")
    sup_del = facilities_by_code.get("SUP-DEL-01")

    # 2. Cyber Assets lookup
    assets_by_code = {a.asset_code: a for a in db.scalars(select(CyberAsset)).all()}

    # 3. Seed Suppliers
    suppliers_data = [
        ("SUP-DEL-01", "Delhi Supplier Gateway", "LOGISTICS_GATEWAY", "Primary regional supplier hub providing inventory manifests and EDI interfaces.", "Rohan Kapoor", 8, "TIER_1", "ASSESSED", "api-ops@delhigateway.in", "https://evidence.delhigateway.in/soc2", "RESTRICTED", 35, "MODERATE"),
        ("SUP-AHM-01", "Ahmedabad Supplier Park", "RAW_PARTS", "Western manufacturing hub supply link for packaging goods and hardware spares.", "Kavita Patel", 7, "TIER_1", "ASSESSED", "security@ahmedabadpark.org", "https://evidence.ahmedabadpark.org/iso27001", "MEDIUM", 28, "MODERATE"),
        ("SUP-LOG-01", "LogixRoute Telematics Systems", "FLEET_SOFTWARE", "Third-party SaaS platform powering vehicle GPS trackers, route optimization, and transit seals.", "Vikram Mehta", 9, "TIER_1", "PENDING_REVIEW", "compliance@logixroute.io", None, "HIGH", 68, "HIGH"),
        ("SUP-IOT-01", "ApexSens IoT & Robotics Automation", "OT_HARDWARE", "Manufacturer of warehouse conveyor PLCs, robotic sorting firmware, and RFID dock portals.", "Dr. Anil Sharma", 9, "TIER_1", "INCOMPLETE", "support@apexsens.tech", None, "RESTRICTED", 74, "HIGH"),
        ("SUP-SEC-01", "CloudGate Identity & MFA Provider", "SECURITY_SAAS", "Enterprise identity provider handling employee single sign-on, warehouse portal MFA, and API tokens.", "Pooja Verma", 10, "TIER_1", "ASSESSED", "security@cloudgate.com", "https://cloudgate.com/security/report-2026", "HIGH", 18, "LOW"),
    ]

    suppliers_map = {}
    for code, name, cat, desc, owner, crit, tier, status, email, ev_url, sens, r_score, r_lvl in suppliers_data:
        sup = Supplier(
            code=code, name=name, category=cat, description=desc, business_owner=owner,
            criticality=crit, tier=tier, assessment_status=status, contact_email=email,
            last_assessment_date="2026-08-15" if status == "ASSESSED" else None,
            evidence_url=ev_url, data_sensitivity=sens, risk_score=r_score, risk_level=r_lvl,
            notes="Evaluated under NEXORA Supply Chain Vendor Resilience Standard v2.4"
        )
        db.add(sup)
        suppliers_map[code] = sup

    db.flush()

    # 4. Seed Software Projects
    wms_prj = SoftwareProject(
        code="PRJ-WMS-CORE",
        name="NEXORA Warehouse Management System (WMS)",
        description="Core enterprise service orchestrating order allocation, packing queues, and automated sorting at primary fulfillment centers.",
        version="4.2.1",
        repository_url="https://github.com/nexora-ops/wms-core",
        business_owner="Anita Sharma (Warehouse Ops)",
        facility_id=fc_jpr.id if fc_jpr else None,
        criticality=9,
    )
    fleet_prj = SoftwareProject(
        code="PRJ-FLEET-TRACK",
        name="Nexora Fleet Telematics & GPS Transit Relay",
        description="Ingestion microservice receiving live truck telemetry, driver breadcrumbs, and automated delivery ETA updates.",
        version="2.8.0",
        repository_url="https://github.com/nexora-ops/fleet-telematics",
        business_owner="Rajesh K. (Fleet Operations)",
        facility_id=fc_jpr.id if fc_jpr else None,
        criticality=8,
    )
    scada_prj = SoftwareProject(
        code="PRJ-IOT-EDGE",
        name="EdgeSCADA Conveyor & Robotics Controller",
        description="Embedded runtime executed on edge gateways to control Modbus PLCs, automated sorters, and high-speed robotic picking arms.",
        version="1.14.3",
        repository_url="https://github.com/nexora-ops/edgescada-firmware",
        business_owner="OT Automation Team",
        facility_id=fc_jpr.id if fc_jpr else None,
        criticality=9,
    )

    db.add_all([wms_prj, fleet_prj, scada_prj])
    db.flush()

    # 5. Seed SBOM Import Job records
    db.add(SbomImportJob(
        project_id=wms_prj.id,
        filename="wms-core-4.2.1-cyclonedx.json",
        format="CYCLONEDX_JSON",
        status="COMPLETED",
        component_count=18,
        relationship_count=12,
        warnings=["Non-fatal: 2 transitive dependencies lacked explicit license declarations"],
    ))
    db.add(SbomImportJob(
        project_id=fleet_prj.id,
        filename="fleet-telematics-spdx.json",
        format="SPDX_JSON",
        status="COMPLETED",
        component_count=14,
        relationship_count=8,
        warnings=[],
    ))
    db.flush()

    # 6. Seed Software Components
    # WMS Components
    c_log4j = SoftwareComponent(
        project_id=wms_prj.id, supplier_id=suppliers_map["SUP-SEC-01"].id,
        name="log4j-core", version="2.14.1", ecosystem="maven",
        purl="pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
        license="Apache-2.0", direct=True, scope="runtime", risk_score=92, risk_level="CRITICAL",
        raw_metadata={"description": "Apache Log4j Core Logging Utility"}
    )
    c_spring = SoftwareComponent(
        project_id=wms_prj.id, supplier_id=suppliers_map["SUP-SEC-01"].id,
        name="spring-core", version="5.3.17", ecosystem="maven",
        purl="pkg:maven/org.springframework/spring-core@5.3.17",
        license="Apache-2.0", direct=True, scope="runtime", risk_score=85, risk_level="CRITICAL",
        raw_metadata={"description": "Spring Framework Core Module"}
    )
    c_jackson = SoftwareComponent(
        project_id=wms_prj.id,
        name="jackson-databind", version="2.13.0", ecosystem="maven",
        purl="pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.13.0",
        license="Apache-2.0", direct=False, scope="runtime", risk_score=48, risk_level="MODERATE"
    )
    c_pg = SoftwareComponent(
        project_id=wms_prj.id,
        name="postgresql", version="42.4.1", ecosystem="maven",
        purl="pkg:maven/org.postgresql/postgresql@42.4.1",
        license="BSD-2-Clause", direct=True, scope="runtime", risk_score=30, risk_level="MODERATE"
    )
    c_ctext = SoftwareComponent(
        project_id=wms_prj.id,
        name="commons-text", version="1.9", ecosystem="maven",
        purl="pkg:maven/org.apache.commons/commons-text@1.9",
        license="Apache-2.0", direct=False, scope="runtime", risk_score=78, risk_level="CRITICAL"
    )

    # Fleet Components
    c_geopy = SoftwareComponent(
        project_id=fleet_prj.id, supplier_id=suppliers_map["SUP-LOG-01"].id,
        name="geopy", version="2.2.0", ecosystem="pypi",
        purl="pkg:pypi/geopy@2.2.0",
        license="MIT", direct=True, scope="runtime", risk_score=22, risk_level="LOW"
    )
    c_mqtt = SoftwareComponent(
        project_id=fleet_prj.id, supplier_id=suppliers_map["SUP-LOG-01"].id,
        name="paho-mqtt", version="1.5.1", ecosystem="pypi",
        purl="pkg:pypi/paho-mqtt@1.5.1",
        license="EPL-2.0", direct=True, scope="runtime", risk_score=64, risk_level="HIGH"
    )
    c_crypto = SoftwareComponent(
        project_id=fleet_prj.id,
        name="cryptography", version="3.4.8", ecosystem="pypi",
        purl="pkg:pypi/cryptography@3.4.8",
        license="Apache-2.0", direct=False, scope="runtime", risk_score=52, risk_level="HIGH"
    )

    # SCADA Components
    c_pyyaml = SoftwareComponent(
        project_id=scada_prj.id, supplier_id=suppliers_map["SUP-IOT-01"].id,
        name="pyyaml", version="5.3.1", ecosystem="pypi",
        purl="pkg:pypi/pyyaml@5.3.1",
        license="MIT", direct=True, scope="runtime", risk_score=88, risk_level="CRITICAL"
    )
    c_modbus = SoftwareComponent(
        project_id=scada_prj.id, supplier_id=suppliers_map["SUP-IOT-01"].id,
        name="modbus-tk", version="1.1.2", ecosystem="pypi",
        purl="pkg:pypi/modbus-tk@1.1.2",
        license="LGPL-2.1", direct=True, scope="runtime", risk_score=58, risk_level="HIGH"
    )

    db.add_all([c_log4j, c_spring, c_jackson, c_pg, c_ctext, c_geopy, c_mqtt, c_crypto, c_pyyaml, c_modbus])
    db.flush()

    # 7. Seed Dependency Graph Edges
    db.add_all([
        ComponentDependency(project_id=wms_prj.id, parent_id=c_spring.id, child_id=c_log4j.id),
        ComponentDependency(project_id=wms_prj.id, parent_id=c_spring.id, child_id=c_ctext.id),
        ComponentDependency(project_id=wms_prj.id, parent_id=c_spring.id, child_id=c_jackson.id),
        ComponentDependency(project_id=fleet_prj.id, parent_id=c_mqtt.id, child_id=c_crypto.id),
        ComponentDependency(project_id=scada_prj.id, parent_id=c_modbus.id, child_id=c_pyyaml.id),
    ])
    db.flush()

    # 8. Seed Vulnerability Findings
    f_log4shell = ComponentFinding(
        component_id=c_log4j.id,
        vulnerability_id="CVE-2021-44228",
        source="CISA_KEV / OSV",
        severity="CRITICAL",
        cvss_score=10.0,
        cisa_kev=True,
        summary="Remote Code Execution via JNDI message lookup parsing (Log4Shell).",
        details="Apache Log4j2 2.0-beta9 through 2.15.0 JNDI features used in configuration, log messages, and parameters do not protect against attacker-controlled LDAP and other JNDI related endpoints.",
        affected_versions=">=2.0-beta9, <=2.14.1",
        fixed_version="2.17.1",
        status="OPEN",
        confidence="CONFIRMED",
        risk_score=98,
        evidence={
            "cisa_kev_date_added": "2021-12-10",
            "cve_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
            "osv_url": "https://osv.dev/vulnerability/GHSA-j2ge-4hdp-5gcc",
            "vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        }
    )
    f_spring4shell = ComponentFinding(
        component_id=c_spring.id,
        vulnerability_id="CVE-2022-22965",
        source="CISA_KEV / OSV",
        severity="CRITICAL",
        cvss_score=9.8,
        cisa_kev=True,
        summary="Spring Framework RCE via Data Binding on JDK 9+ (Spring4Shell).",
        details="A Spring MVC or Spring WebFlux application running on JDK 9+ may be vulnerable to remote code execution via data binding with specific parameter accessors.",
        affected_versions=">=5.3.0, <=5.3.17",
        fixed_version="5.3.18",
        status="IN_TRIAGE",
        confidence="CONFIRMED",
        risk_score=94,
        evidence={"cisa_kev_date_added": "2022-04-04", "cve_url": "https://nvd.nist.gov/vuln/detail/CVE-2022-22965"}
    )
    f_pyyaml = ComponentFinding(
        component_id=c_pyyaml.id,
        vulnerability_id="CVE-2020-14343",
        source="OSV",
        severity="HIGH",
        cvss_score=8.8,
        cisa_kev=False,
        summary="Arbitrary code execution via full_load / FullLoader object construction.",
        details="A vulnerability was discovered in the PyYAML library in versions before 5.4 where untrusted YAML input allows arbitrary python object instantiation through the FullLoader.",
        affected_versions="<5.4",
        fixed_version="5.4",
        status="OPEN",
        confidence="HIGH",
        risk_score=82,
        evidence={"cve_url": "https://nvd.nist.gov/vuln/detail/CVE-2020-14343"}
    )
    f_ctext = ComponentFinding(
        component_id=c_ctext.id,
        vulnerability_id="CVE-2022-42889",
        source="OSV",
        severity="HIGH",
        cvss_score=8.1,
        cisa_kev=False,
        summary="Apache Commons Text RCE through string interpolation (Text4Shell).",
        details="Apache Commons Text performs variable interpolation, such as '${prefix:name}' where the prefix directs a lookup class. Vulnerable lookups include 'script', 'dns', and 'url'.",
        affected_versions=">=1.5, <=1.9",
        fixed_version="1.10.0",
        status="OPEN",
        confidence="CONFIRMED",
        risk_score=75,
        evidence={"cve_url": "https://nvd.nist.gov/vuln/detail/CVE-2022-42889"}
    )
    f_mqtt = ComponentFinding(
        component_id=c_mqtt.id,
        vulnerability_id="CVE-2021-34434",
        source="OSV",
        severity="MEDIUM",
        cvss_score=6.5,
        cisa_kev=False,
        summary="Denial of Service via crafted MQTT payload loop.",
        details="Malicious brokers or network MITM can send malformed control packets causing client unhandled disconnect loops.",
        affected_versions="<1.6.0",
        fixed_version="1.6.0",
        status="OPEN",
        confidence="HIGH",
        risk_score=55,
        evidence={"cve_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-34434"}
    )

    db.add_all([f_log4shell, f_spring4shell, f_pyyaml, f_ctext, f_mqtt])
    db.flush()

    # 9. Seed Cyber-Physical Deployment Mappings (The Differentiator!)
    dep_log4j = ComponentDeployment(
        component_id=c_log4j.id,
        service_name="Jaipur Warehouse Inventory Service",
        cyber_asset_id=assets_by_code["SRV-INV-JPR"].id if "SRV-INV-JPR" in assets_by_code else None,
        facility_id=fc_jpr.id if fc_jpr else None,
        business_process="Physical Inventory Reservation & Picking Flow",
        mapping_type="VERIFIED",
        notes="Service handles physical stock checks for FC-JPR-01 orders before packing."
    )
    dep_spring = ComponentDeployment(
        component_id=c_spring.id,
        service_name="Order Processing Gateway",
        cyber_asset_id=assets_by_code["DB-ORD-JPR"].id if "DB-ORD-JPR" in assets_by_code else None,
        facility_id=fc_jpr.id if fc_jpr else None,
        business_process="Order Manifest & Customer Checkout Processing",
        mapping_type="VERIFIED",
        notes="Processes incoming orders and dispatches fulfillment records to database."
    )
    dep_yaml = ComponentDeployment(
        component_id=c_pyyaml.id,
        service_name="Conveyor Sorter Controller",
        cyber_asset_id=assets_by_code["PLC-SORT-JPR"].id if "PLC-SORT-JPR" in assets_by_code else None,
        facility_id=fc_jpr.id if fc_jpr else None,
        business_process="Automated Package Sorting & Conveyor Routing",
        mapping_type="VERIFIED",
        notes="Controls sorting bins and PLC sensors at the outbound packing dock."
    )
    dep_mqtt = ComponentDeployment(
        component_id=c_mqtt.id,
        service_name="OT Telemetry Ingestion Gateway",
        cyber_asset_id=assets_by_code["OT-GW-JPR"].id if "OT-GW-JPR" in assets_by_code else None,
        facility_id=fc_jpr.id if fc_jpr else None,
        business_process="IoT RFID & Environmental Dock Verification",
        mapping_type="VERIFIED",
        notes="Aggregates RFID package scan feeds from loading bays."
    )
    dep_geopy = ComponentDeployment(
        component_id=c_geopy.id,
        service_name="Fleet GPS Transit Relay",
        cyber_asset_id=assets_by_code["GPS-TRK-001"].id if "GPS-TRK-001" in assets_by_code else None,
        facility_id=fc_jpr.id if fc_jpr else None,
        business_process="Delivery Fleet In-Transit Tracking & Seal Integrity",
        mapping_type="USER_MAPPED",
        notes="Calculates transit distance, velocity, and driver location updates."
    )

    db.add_all([dep_log4j, dep_spring, dep_yaml, dep_mqtt, dep_geopy])
    db.flush()

    # 10. Seed Mitigation Actions
    db.add_all([
        MitigationAction(
            finding_id=f_log4shell.id, component_id=c_log4j.id,
            title="Upgrade log4j-core to v2.17.1 and set formatMsgNoLookups=true",
            action_type="UPGRADE_VERSION", status="IN_PROGRESS",
            notes="Patch scheduled for deployment during low-volume maintenance window (02:00 AM IST)."
        ),
        MitigationAction(
            finding_id=f_spring4shell.id, component_id=c_spring.id,
            title="Upgrade Spring Framework to 5.3.18 and enforce WAF request filters",
            action_type="COMPENSATING_CONTROL", status="PROPOSED",
            notes="WAF inspection rule activated on edge reverse proxy as interim mitigation."
        ),
        MitigationAction(
            finding_id=f_pyyaml.id, component_id=c_pyyaml.id,
            title="Refactor YAML parsing to yaml.safe_load() in SCADA controller driver",
            action_type="UPGRADE_VERSION", status="COMPLETED",
            notes="Verified safe loader eliminates arbitrary class constructor execution."
        ),
        MitigationAction(
            supplier_id=suppliers_map["SUP-LOG-01"].id,
            title="Request updated SOC 2 Type II assurance report from LogixRoute",
            action_type="SUPPLIER_AUDIT", status="PROPOSED",
            notes="Assessment overdue by 45 days. Vendor notified."
        ),
    ])

    # 11. Seed Risk Snapshots
    db.add(RiskSnapshot(
        entity_type="PROJECT",
        entity_id=wms_prj.id,
        risk_score=84,
        risk_level="CRITICAL",
        factor_breakdown={
            "vulnerability_severity": {"factor_score": 100.0, "weight": 0.25, "contribution": 25.0},
            "known_exploitation": {"factor_score": 100.0, "weight": 0.20, "contribution": 20.0},
            "business_criticality": {"factor_score": 90.0, "weight": 0.20, "contribution": 18.0},
            "dependency_exposure": {"factor_score": 75.0, "weight": 0.15, "contribution": 11.25},
            "supplier_risk": {"factor_score": 35.0, "weight": 0.10, "contribution": 3.5},
            "data_sensitivity": {"factor_score": 75.0, "weight": 0.10, "contribution": 7.5},
        },
        available_factors=["vulnerability_severity", "known_exploitation", "business_criticality", "dependency_exposure", "supplier_risk", "data_sensitivity"],
        missing_factors=[],
        rationale="WMS Core carries Critical risk due to weaponized CISA KEV vulnerability (CVE-2021-44228) deployed on inventory server.",
    ))

    db.commit()
    print("[+] SupplyLens AI synthetic demo datasets successfully seeded!", flush=True)
