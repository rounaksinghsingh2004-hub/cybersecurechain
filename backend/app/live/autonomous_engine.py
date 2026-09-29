"""
Autonomous Red vs Blue Cyber Engine — Digital Twin Automated Attack & Defense.

Coordinates:
- Autonomous Adversary (Red Team AI): Launches realistic multi-stage campaigns
- Real-time ML IDS: Classifies live network traffic flows
- Autonomous SOAR (Blue Team AI): Executes dynamic containment, order rerouting,
  and recovery playbooks without requiring manual human clicks.
"""
import asyncio
import random
import time
from datetime import datetime
from typing import Callable, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CyberAsset, Facility, Incident, Order, SecurityControl
from app.services.events import EventService


ADVERSARY_PROFILES = [
    {"name": "APT-29 (CozyBear)", "origin": "State-Sponsored", "tactic": "Stealth Infiltration & Lateral Movement"},
    {"name": "LockBit 3.0 Syndicate", "origin": "Cybercrime Cartel", "tactic": "Ransomware & OT Interruption"},
    {"name": "FIN7 Financial", "origin": "Organized Group", "tactic": "Inventory & Payment Portal Manipulation"},
    {"name": "Volt Typhoon", "origin": "Critical Infrastructure", "tactic": "IoT Firmware & SCADA Disruption"},
    {"name": "Lazarus Unit 180", "origin": "Strategic Operations", "tactic": "Fleet GPS Spoofing & Supply Hijack"},
]

ATTACK_SCENARIOS = [
    {
        "scenario": "DATABASE_EXFILTRATION",
        "vector": "Web Attack - Sql Injection",
        "description": "SQL Injection on legacy warehouse API attempting to exfiltrate inventory and shipping manifests",
        "playbook": "PLAYBOOK_DB_ISOLATION",
        "defensive_steps": [
            "Detect SQLi payload via ML WAF inspection",
            "Sever external connections to primary DB cluster",
            "Failover warehouse reads to immutable read-replica",
            "Force session invalidation for all active API keys",
        ],
    },
    {
        "scenario": "RANSOMWARE_IMPACT",
        "vector": "Bot",
        "description": "Lateral propagation of ransomware payload encrypting localized fulfillment records",
        "playbook": "PLAYBOOK_RANSOMWARE_CONTAINMENT",
        "defensive_steps": [
            "Identify rapid file-encryption IO patterns via Endpoint ML",
            "Isolate infected VLAN from Corporate and OT networks",
            "Restore corrupted ledger blocks from verified backups",
            "Reroute incoming truck deliveries to alternate hubs",
        ],
    },
    {
        "scenario": "OT_DISRUPTION",
        "vector": "DDoS",
        "description": "High-volume SYN/UDP flood directed at warehouse programmable logic controllers (PLCs)",
        "playbook": "PLAYBOOK_OT_CONTAINMENT",
        "defensive_steps": [
            "Enable Rate-Limiting Filter on Edge Router",
            "Micro-segment OT Network Boundary from IT Corporate Subnet",
            "Failover Conveyor and Sorter PLC to Local Isolated Controller",
            "Reroute Critical Shipments to Nearest Healthy Fulfillment Center",
        ],
    },
    {
        "scenario": "ACCOUNT_COMPROMISE",
        "vector": "SSH-Patator",
        "description": "Distributed dictionary credential attack against warehouse supervisor portal",
        "playbook": "PLAYBOOK_IDENTITY_LOCKDOWN",
        "defensive_steps": [
            "Detect Anomalous Authentication Velocity via IDS ML",
            "Revoke Active Session Token and Enforce Step-up MFA",
            "Apply Least-Privilege Scope Restriction on Warehouse Role",
            "Notify Security Operations Center and Audit Identity Logs",
        ],
    },
    {
        "scenario": "INVENTORY_MANIPULATION",
        "vector": "Web Attack - Brute Force",
        "description": "Exploitation of web inventory API attempting unauthorized stock allocation adjustments",
        "playbook": "PLAYBOOK_WAF_INSPECTION",
        "defensive_steps": [
            "Inject Dynamic WAF Rule blocking malicious request patterns",
            "Lock Inventory Mutation Privileges to Read-Only Sandbox",
            "Audit Stock Ledger against Immutable Event Hash Chain",
            "Restore Inventory Reservation State from Last Verified Checkpoint",
        ],
    },
    {
        "scenario": "QR_TAMPERING",
        "vector": "PortScan",
        "description": "TCP SYN stealth port scan probing fulfillment scanning terminals and barcode relays",
        "playbook": "PLAYBOOK_NETWORK_SURFACE_HARDENING",
        "defensive_steps": [
            "Identify Port Reconnaissance Signature via CIC-IDS2017 Model",
            "Blackhole Attacking Source Subnet at Perimeter Gateway",
            "Enforce Mutual TLS (mTLS) on All Handheld Scanner Relays",
            "Verify Integrity of Last Scanned Package Barcodes",
        ],
    },
    {
        "scenario": "IOT_SPOOFING",
        "vector": "Bot",
        "description": "Compromised smart temperature/humidity sensors emitting corrupted telemetry",
        "playbook": "PLAYBOOK_IOT_DEVICE_QUARANTINE",
        "defensive_steps": [
            "Detect Mirai-style Bot Telemetry Anomaly via Machine Learning",
            "Quarantine Outlier Sensor MAC Addresses into Honeynet VLAN",
            "Switch Cold-Chain Verification to Auxiliary Backup Sensors",
            "Verify Perishable Goods Temperature Logs",
        ],
    },
    {
        "scenario": "GPS_SPOOFING",
        "vector": "DDoS",
        "description": "Signal denial-of-service and fake coordinate broadcast targeting fleet transit vehicles",
        "playbook": "PLAYBOOK_FLEET_INTEGRITY_SAFEGUARD",
        "defensive_steps": [
            "Detect GPS Jamming and Anomalous Velocity Jitter",
            "Switch Fleet Telemetry to Cellular Tower Triangulation Fallback",
            "Re-verify Truck Seal Status via Driver Challenge Handshake",
            "Normalize Vehicle Location and Dispatch ETA",
        ],
    },
]

FACILITY_FALLBACKS = {
    "FC-JPR-01": "HUB-DEL-01",
    "HUB-DEL-01": "FC-JPR-01",
    "MFG-PUN-01": "HUB-BOM-01",
    "HUB-BOM-01": "MFG-PUN-01",
    "WH-BLR-01": "HUB-CHN-01",
    "HUB-CHN-01": "WH-BLR-01",
    "FC-KOL-01": "HUB-DEL-01",
    "FC-HYD-01": "WH-BLR-01",
}


class AutonomousDefenseEngine:
    """
    Singleton engine managing the automated cyber duel on the supply chain digital twin.
    """

    def __init__(self):
        self.adversary_enabled = False
        self.mitigation_enabled = True
        self.speed = "normal"  # "fast": 8s, "normal": 20s, "relaxed": 35s
        self.last_campaign_time = 0.0
        self.current_campaign = None
        self.campaign_history = []
        self.total_attacks = 0
        self.total_detected = 0
        self.total_mitigated = 0
        self.total_orders_protected = 0
        self.total_financial_saved_inr = 0
        self._mitigation_timer: Optional[asyncio.Task] = None
        self._campaign_counter = 100

    def get_interval(self) -> float:
        if self.speed == "fast":
            return 8.0
        elif self.speed == "relaxed":
            return 35.0
        return 20.0

    def get_status(self) -> dict:
        return {
            "adversary_enabled": self.adversary_enabled,
            "mitigation_enabled": self.mitigation_enabled,
            "speed": self.speed,
            "current_campaign": self.current_campaign,
            "history": self.campaign_history[-10:],
            "metrics": {
                "total_attacks": self.total_attacks,
                "total_detected": self.total_detected,
                "total_mitigated": self.total_mitigated,
                "mitigation_rate": round(
                    (self.total_mitigated / max(1, self.total_attacks)) * 100, 1
                ),
                "total_orders_protected": self.total_orders_protected,
                "total_financial_saved_inr": self.total_financial_saved_inr,
            },
        }

    async def launch_campaign(
        self,
        db: Session,
        traffic_gen,
        broadcast: Callable,
        forced_scenario: Optional[str] = None,
        forced_facility: Optional[str] = None,
    ):
        """Initiate an automated adversary campaign against a digital twin node."""
        facilities = db.scalars(select(Facility)).all()
        if not facilities:
            return None

        facility = None
        if forced_facility:
            facility = db.scalar(select(Facility).where(Facility.code == forced_facility))
        if not facility:
            facility = random.choice(facilities)

        # Select attack scenario
        scenario_info = None
        if forced_scenario:
            scenario_info = next(
                (s for s in ATTACK_SCENARIOS if s["scenario"] == forced_scenario), None
            )
        if not scenario_info:
            scenario_info = random.choice(ATTACK_SCENARIOS)

        # Select target asset in that facility
        target_asset = db.scalars(
            select(CyberAsset).where(CyberAsset.facility_id == facility.id)
        ).first()

        profile = random.choice(ADVERSARY_PROFILES)
        self._campaign_counter += 1
        campaign_id = f"AUTOCAMP-{self._campaign_counter}"

        # Estimate potential orders at risk in this facility
        orders_count = db.query(Order).filter(Order.origin_facility_id == facility.id).count()
        if orders_count == 0:
            orders_count = random.randint(12, 35)

        estimated_loss = orders_count * random.randint(3200, 5800) + random.randint(50000, 150000)

        self.current_campaign = {
            "id": campaign_id,
            "adversary": profile["name"],
            "adversary_origin": profile["origin"],
            "adversary_tactic": profile["tactic"],
            "scenario": scenario_info["scenario"],
            "attack_vector": scenario_info["vector"],
            "description": scenario_info["description"],
            "facility_code": facility.code,
            "facility_name": facility.name,
            "facility_city": facility.city,
            "target_asset_code": target_asset.asset_code if target_asset else "SYS-GATEWAY",
            "target_asset_name": target_asset.name if target_asset else "Core Switch",
            "stage": "ATTACK_IN_PROGRESS",
            "started_at": datetime.utcnow().isoformat(),
            "detected_at": None,
            "mitigated_at": None,
            "playbook": scenario_info["playbook"],
            "defensive_steps": scenario_info["defensive_steps"],
            "orders_at_risk": orders_count,
            "orders_rerouted": 0,
            "estimated_loss_inr": estimated_loss,
            "detection_confidence": None,
            "mitigation_status": "MONITORING",
        }

        self.total_attacks += 1
        self.last_campaign_time = time.time()

        # Inject into traffic generator
        traffic_gen.inject_attack(
            facility.code, scenario_info["scenario"], duration_seconds=45.0
        )

        EventService.record(
            db,
            "AUTONOMOUS_ADVERSARY_ATTACK",
            "CYBER",
            "facility",
            facility.code,
            f"Adversary [{profile['name']}] launched [{scenario_info['vector']}] attack on {facility.code} ({facility.name})",
            facility.code,
            "ADVERSARY_AI",
        )
        db.commit()

        # Broadcast campaign start
        await broadcast({
            "type": "CAMPAIGN_LAUNCHED",
            "campaign": self.current_campaign,
            "message": f"Adversary [{profile['name']}] attacking {facility.code} using {scenario_info['vector']}!",
        })

        return self.current_campaign

    async def handle_detection(self, event_data: dict, db: Session, broadcast: Callable):
        """Called when the live ML IDS classifies an attack in real time."""
        if not self.current_campaign:
            return

        if self.current_campaign["stage"] == "ATTACK_IN_PROGRESS":
            self.current_campaign["stage"] = "ML_IDS_DETECTED"
            self.current_campaign["detected_at"] = datetime.utcnow().isoformat()
            self.current_campaign["detection_confidence"] = event_data.get("confidence", 0.95)
            self.total_detected += 1

            await broadcast({
                "type": "CAMPAIGN_DETECTED",
                "campaign": self.current_campaign,
                "confidence": self.current_campaign["detection_confidence"],
                "message": f"ML IDS identified {event_data.get('label')} with {self.current_campaign['detection_confidence']*100:.1f}% confidence!",
            })

            # If auto mitigation is enabled, schedule execution in 2.5 seconds
            if self.mitigation_enabled:
                if self._mitigation_timer and not self._mitigation_timer.done():
                    self._mitigation_timer.cancel()
                self._mitigation_timer = asyncio.create_task(
                    self._delayed_mitigation(db, broadcast)
                )

    async def _delayed_mitigation(self, db: Session, broadcast: Callable):
        """Execute autonomous SOAR mitigation after a realistic 3-second containment analysis."""
        await asyncio.sleep(3.0)
        from app.main import traffic_gen  # Lazy import to avoid circular dependency
        await self.execute_soar_defense(db, traffic_gen, broadcast)

    async def execute_soar_defense(self, db: Session, traffic_gen, broadcast: Callable):
        """Executes full autonomous Blue Team response playbook and reroutes orders."""
        if not self.current_campaign:
            return

        camp = self.current_campaign
        facility_code = camp["facility_code"]
        facility = db.scalar(select(Facility).where(Facility.code == facility_code))
        fallback_code = FACILITY_FALLBACKS.get(facility_code, "HUB-DEL-01")

        # 1. Reroute affected orders to fallback healthy facility in the Digital Twin
        orders_protected = 0
        if facility:
            fallback_facility = db.scalar(select(Facility).where(Facility.code == fallback_code))
            if fallback_facility:
                orders = db.scalars(
                    select(Order)
                    .where(Order.origin_facility_id == facility.id)
                    .where(Order.cyber_status.in_(["UNDER_ATTACK", "CLEAR"]))
                    .limit(camp["orders_at_risk"])
                ).all()

                for o in orders:
                    o.cyber_status = "REROUTED_SECURE"
                    orders_protected += 1

        if orders_protected == 0:
            orders_protected = camp["orders_at_risk"]

        # 2. Recover all assets in the facility
        if facility:
            assets = db.scalars(
                select(CyberAsset).where(CyberAsset.facility_id == facility.id)
            ).all()
            for a in assets:
                a.compromised = False

        # 3. Stop traffic injection
        traffic_gen.clear_attack(facility_code)

        # 4. Resolve active incidents for this facility
        incidents = db.scalars(
            select(Incident).where(
                Incident.facility_code == facility_code, Incident.status != "RECOVERED"
            )
        ).all()
        for inc in incidents:
            inc.status = "RECOVERED"
            inc.actions = [
                *inc.actions,
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "SOAR_AUTONOMOUS_MITIGATION",
                    "note": f"Executed playbook {camp['playbook']}: {', '.join(camp['defensive_steps'][:2])}",
                },
            ]

        # 5. Record Blue Team Defense Event
        EventService.record(
            db,
            "SOAR_AUTONOMOUS_DEFENSE",
            "RECOVERY",
            "facility",
            facility_code,
            f"Autonomous SOAR executed [{camp['playbook']}]. Rerouted {orders_protected} orders to {fallback_code}. Facility {facility_code} restored to HEALTHY.",
            facility_code,
            "BLUE_TEAM_SOAR",
        )
        db.commit()

        # Update statistics
        camp["stage"] = "MITIGATED"
        camp["mitigated_at"] = datetime.utcnow().isoformat()
        camp["orders_rerouted"] = orders_protected
        camp["mitigation_status"] = "SUCCESSFUL"
        
        self.total_mitigated += 1
        self.total_orders_protected += orders_protected
        self.total_financial_saved_inr += camp["estimated_loss_inr"]

        # Append to history
        self.campaign_history.append(dict(camp))
        if len(self.campaign_history) > 20:
            self.campaign_history.pop(0)

        # Broadcast mitigation event
        await broadcast({
            "type": "CAMPAIGN_MITIGATED",
            "campaign": camp,
            "orders_protected": orders_protected,
            "fallback_facility": fallback_code,
            "financial_saved_inr": camp["estimated_loss_inr"],
            "message": f"Autonomous SOAR neutralized threat at {facility_code}! Rerouted {orders_protected} orders to {fallback_code}.",
        })


autonomous_engine = AutonomousDefenseEngine()
