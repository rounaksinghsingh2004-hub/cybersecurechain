"""
Asset State Machine — manages real-time state transitions when the live
ML traffic scanner detects an attack.

Handles:
- Flipping CyberAsset.compromised = True
- Propagating compromise to connected assets in the same facility
- Auto-creating Incident records
- Freezing affected Orders (cyber_status = UNDER_ATTACK)
- Auto-responding if ML confidence > AUTO_RESPOND_THRESHOLD
"""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import CyberAsset, Event, Incident, Order


AUTO_RESPOND_THRESHOLD = 0.95  # above this, auto-isolate fires


class AssetStateMachine:

    def __init__(self, db: Session):
        self.db = db

    def compromise_asset(self, asset: CyberAsset, attack_label: str, confidence: float) -> Incident | None:
        """
        Mark an asset as compromised, freeze its facility's orders, log an event,
        and auto-create an Incident. Returns the Incident if newly created, else None.
        """
        if asset.compromised:
            return None  # Already compromised, skip

        # 1. Flip the asset state
        asset.compromised = True

        # 2. Freeze active orders from this facility
        if asset.facility_id:
            self.db.execute(
                Order.__table__.update()
                .where(Order.origin_facility_id == asset.facility_id)
                .where(Order.cyber_status == "CLEAR")
                .values(cyber_status="UNDER_ATTACK")
            )

        # 3. Log a cyber event
        self.db.add(Event(
            event_type="CYBER_ASSET_COMPROMISED",
            category="cyber",
            entity_type="cyber_asset",
            entity_id=str(asset.id),
            facility_code=asset.facility.code if asset.facility else "UNKNOWN",
            source="LIVE_IDS_ML",
            description=f"[ML LIVE DETECTION] {asset.asset_code} classified as {attack_label} (confidence {confidence:.1%}). Asset marked COMPROMISED.",
            previous_state={"compromised": False},
            new_state={"compromised": True, "label": attack_label, "confidence": confidence},
        ))

        # 4. Auto-create an Incident
        import random, string
        code = "INC-" + "".join(random.choices(string.digits, k=6))
        severity = "CRITICAL" if confidence > 0.9 else "HIGH"
        incident = Incident(
            code=code,
            severity=severity,
            status="DETECTED",
            facility_code=asset.facility.code if asset.facility else "UNKNOWN",
            summary=f"Live IDS ML detected {attack_label} originating from {asset.asset_code}. Auto-generated at {datetime.utcnow().strftime('%H:%M:%S UTC')}.",
            actions=[{
                "timestamp": datetime.utcnow().isoformat(),
                "action": "AUTO_DETECTED",
                "note": f"ML model classified traffic as {attack_label} with {confidence:.1%} confidence.",
            }],
        )
        self.db.add(incident)

        # 5. Auto-respond if confidence is very high
        if confidence >= AUTO_RESPOND_THRESHOLD:
            incident.actions.append({
                "timestamp": datetime.utcnow().isoformat(),
                "action": "AUTO_ISOLATE",
                "note": f"Confidence {confidence:.1%} exceeded threshold {AUTO_RESPOND_THRESHOLD:.0%}. Asset automatically isolated.",
            })
            incident.status = "CONTAINED"
            self.db.add(Event(
                event_type="AUTO_RESPONSE_EXECUTED",
                category="cyber",
                entity_type="incident",
                entity_id=code,
                facility_code=incident.facility_code,
                source="LIVE_IDS_ML",
                description=f"Auto-response: ISOLATE_ASSET executed on {asset.asset_code} (confidence {confidence:.1%} > threshold).",
                previous_state=None,
                new_state={"action": "AUTO_ISOLATE", "confidence": confidence},
            ))

        self.db.commit()
        return incident

    def propagate_attack(self, facility_id: int, attack_label: str, confidence: float):
        """
        Spread compromise to ALL assets in the same facility that aren't already compromised.
        Called a few seconds after the initial detection to simulate lateral movement.
        """
        assets = self.db.scalars(
            select(CyberAsset)
            .where(CyberAsset.facility_id == facility_id)
            .where(CyberAsset.compromised == False)
        ).all()

        for asset in assets:
            asset.compromised = True
            self.db.add(Event(
                event_type="CYBER_PROPAGATION",
                category="cyber",
                entity_type="cyber_asset",
                entity_id=str(asset.id),
                facility_code=asset.facility.code if asset.facility else "UNKNOWN",
                source="LIVE_IDS_ML",
                description=f"[PROPAGATION] {asset.asset_code} reached by lateral movement from {attack_label} attack.",
                previous_state={"compromised": False},
                new_state={"compromised": True},
            ))

        self.db.commit()

    def recover_facility(self, facility_id: int):
        """Reset all assets in a facility back to CLEAR after an attack ends."""
        assets = self.db.scalars(
            select(CyberAsset).where(CyberAsset.facility_id == facility_id)
        ).all()
        for asset in assets:
            asset.compromised = False

        # Un-freeze orders
        self.db.execute(
            Order.__table__.update()
            .where(Order.origin_facility_id == facility_id)
            .where(Order.cyber_status == "UNDER_ATTACK")
            .values(cyber_status="CLEAR")
        )
        self.db.commit()
