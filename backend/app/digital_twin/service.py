from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.models import CyberAsset, Event, Facility, Inventory, Order, Shipment, Vehicle


class DigitalTwinService:
    def __init__(self, db: Session):
        self.db = db

    def get_global_state(self) -> dict:
        facilities = self.db.scalars(select(Facility)).all()
        inventory_units = self.db.scalar(select(func.sum(Inventory.available))) or 0
        active_orders = self.db.scalar(select(func.count()).select_from(Order).where(Order.status != "DELIVERED")) or 0
        compromised = self.db.scalar(select(func.count()).select_from(CyberAsset).where(CyberAsset.compromised.is_(True))) or 0
        return {
            "metrics": {
                "facilities": len(facilities), "active_orders": active_orders,
                "shipments": self.db.scalar(select(func.count()).select_from(Shipment)) or 0,
                "vehicles": self.db.scalar(select(func.count()).select_from(Vehicle)) or 0,
                "inventory_units": inventory_units, "compromised_assets": compromised,
            },
            "facilities": [self._facility(f) for f in facilities],
            "relationships": self.get_relationships(),
            "recent_events": self.get_recent_events(16),
        }

    def _facility(self, f: Facility) -> dict:
        return {"id": f.id, "code": f.code, "name": f.name, "type": f.type, "city": f.city,
                "latitude": f.latitude, "longitude": f.longitude, "status": f.status,
                "capacity": f.capacity, "cyber_risk": f.cyber_risk}

    def get_facility_state(self, facility_id: int) -> dict:
        f = self.db.get(Facility, facility_id)
        if not f:
            raise ValueError("Facility not found")
        inventory = self.db.scalars(select(Inventory).where(Inventory.facility_id == facility_id)).all()
        assets = self.db.scalars(select(CyberAsset).where(CyberAsset.facility_id == facility_id)).all()
        orders = self.db.scalars(select(Order).where(Order.origin_facility_id == facility_id)).all()
        return {"facility": self._facility(f), "inventory": [{"sku": i.product.sku, "product": i.product.name, "available": i.available, "reserved": i.reserved, "batch": i.batch_code} for i in inventory],
                "orders": [{"number": o.number, "status": o.status, "destination": o.destination} for o in orders],
                "assets": [{"id": a.id, "name": a.name, "type": a.asset_type, "compromised": a.compromised} for a in assets],
                "activity": self.get_recent_events(25, f.code)}

    def get_relationships(self) -> list[dict]:
        facilities = self.db.scalars(select(Facility)).all()
        by_type = {}
        for f in facilities:
            by_type.setdefault(f.type, []).append(f)
        flow = ["SUPPLIER", "FACTORY", "WAREHOUSE", "DISTRIBUTION_CENTER", "DELIVERY_HUB"]
        edges = []
        for left, right in zip(flow, flow[1:]):
            for source in by_type.get(left, [])[:2]:
                for target in by_type.get(right, [])[:2]:
                    edges.append({"source": source.code, "target": target.code, "type": "DEPENDS_ON"})
        return edges

    def get_recent_events(self, limit: int = 20, facility_code: str | None = None) -> list[dict]:
        query = select(Event).order_by(Event.created_at.desc()).limit(limit)
        if facility_code:
            query = select(Event).where(Event.facility_code == facility_code).order_by(Event.created_at.desc()).limit(limit)
        return [{"id": e.id, "type": e.event_type, "category": e.category, "description": e.description,
                 "facility": e.facility_code, "source": e.source, "timestamp": e.created_at.isoformat()} for e in self.db.scalars(query).all()]

    def get_cyber_state(self) -> dict:
        assets = self.db.scalars(select(CyberAsset)).all()
        risk = [risk_score(a) for a in assets]
        return {"assets": [asset_payload(a) for a in assets], "posture": max(0, round(100 - (sum(risk) / max(1, len(risk))))),
                "critical_assets": sum(a.criticality >= 8 for a in assets), "high_risk_assets": sum(r >= 61 for r in risk)}


def risk_score(asset: CyberAsset) -> int:
    return min(100, round((asset.likelihood * asset.exposure * asset.criticality * asset.impact) / 100))


def risk_level(score: int) -> str:
    return "CRITICAL" if score >= 81 else "HIGH" if score >= 61 else "MEDIUM" if score >= 31 else "LOW"


def asset_payload(asset: CyberAsset) -> dict:
    score = risk_score(asset)
    return {"id": asset.id, "code": asset.asset_code, "name": asset.name, "type": asset.asset_type,
            "facility": asset.facility.code if asset.facility else "External", "criticality": asset.criticality,
            "exposure": asset.exposure, "vulnerabilities": asset.vulnerabilities, "controls": asset.controls,
            "compromised": asset.compromised, "risk": score, "risk_level": risk_level(score),
            "why": f"Likelihood {asset.likelihood}/10 x exposure {asset.exposure}/10 x criticality {asset.criticality}/10 x impact {asset.impact}/10.",
            "recommendation": ", ".join(asset.controls) if asset.controls else "Enable monitoring and least-privilege access."}

