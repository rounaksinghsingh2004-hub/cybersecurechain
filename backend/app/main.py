import asyncio
import random
import time
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.database import SessionLocal, get_db, initialize_database
from app.digital_twin.service import DigitalTwinService, asset_payload
from app.live.autonomous_engine import autonomous_engine
from app.live.state_machine import AssetStateMachine
from app.live.traffic import TrafficGenerator
from app.models import CyberAsset, Employee, Event, Facility, Incident, Inventory, OperationalAsset, Order, Product, SecurityControl, Shipment, Simulation, Vehicle
from app.seed import seed
from app.services.operations import OperationsService
from app.simulation.engine import SimulationEngine


# ---------------------------------------------------------------------------
# WebSocket Connection Manager — broadcasts to all connected browser clients
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()
traffic_gen = TrafficGenerator()


# ---------------------------------------------------------------------------
# Background live scanner — runs every 3 s, scores traffic, broadcasts events
# ---------------------------------------------------------------------------

async def live_scanner():
    """
    Continuously generates and scores synthetic network traffic for each
    monitored facility. Broadcasts every event over WebSocket. When an attack
    is detected, triggers the asset state machine to update the DB and sends
    a high-priority ATTACK alert to the frontend.
    """
    # Track which facilities we've already fired propagation for (reset on recovery)
    propagated: set[int] = set()
    tick_count = 0

    while True:
        await asyncio.sleep(2.5)
        tick_count += 1
        db = SessionLocal()
        try:
            # 1. Check Autonomous Adversary AI
            if autonomous_engine.adversary_enabled:
                now = time.time()
                active_attacks = traffic_gen.active_attacks()
                if not active_attacks and (now - autonomous_engine.last_campaign_time) > autonomous_engine.get_interval():
                    await autonomous_engine.launch_campaign(db, traffic_gen, manager.broadcast)

            facilities = db.scalars(select(Facility).limit(20)).all()
            if not facilities:
                continue

            # Pick a random subset of facilities to scan each tick
            sample = random.sample(facilities, min(3, len(facilities)))

            for facility in sample:
                # Get a representative cyber asset for this facility
                asset = db.scalars(
                    select(CyberAsset).where(CyberAsset.facility_id == facility.id).limit(1)
                ).first()
                if not asset:
                    continue

                event = traffic_gen.generate(facility.code, asset.asset_code)

                payload = {
                    "type": "ATTACK_DETECTED" if event.is_attack else "TRAFFIC_NORMAL",
                    "facility_code": event.facility_code,
                    "asset_code": event.asset_code,
                    "label": event.label,
                    "confidence": event.confidence,
                    "is_attack": event.is_attack,
                    "scenario": event.scenario,
                    "timestamp": event.timestamp,
                    "packet_features": event.packet_features,
                }

                if event.is_attack and event.confidence > 0.4:
                    # Trigger state machine — compromise asset, create incident
                    sm = AssetStateMachine(db)
                    incident = sm.compromise_asset(asset, event.label, event.confidence)

                    if incident:
                        payload["incident_code"] = incident.code
                        payload["incident_severity"] = incident.severity
                        payload["auto_responded"] = incident.status == "CONTAINED"

                    # Notify autonomous engine of ML detection
                    await autonomous_engine.handle_detection(payload, db, manager.broadcast)

                    # Schedule propagation after 8 seconds if not already propagated
                    if facility.id not in propagated:
                        propagated.add(facility.id)
                        asyncio.create_task(
                            _delayed_propagation(facility.id, event.label, event.confidence)
                        )
                else:
                    # Normal traffic — if facility was previously attacked, recover it
                    if facility.id in propagated and not traffic_gen._attack_injections.get(facility.code):
                        sm = AssetStateMachine(db)
                        sm.recover_facility(facility.id)
                        propagated.discard(facility.id)
                        payload["type"] = "FACILITY_RECOVERED"

                await manager.broadcast(payload)

            # 2. Dynamic Operational Twin Telemetry (every ~5 seconds)
            if tick_count % 2 == 0:
                vehicles = db.scalars(select(Vehicle)).all()
                for v in vehicles:
                    v.reported_latitude += random.uniform(-0.003, 0.003)
                    v.reported_longitude += random.uniform(-0.003, 0.003)
                    v.current_latitude = v.reported_latitude
                    v.current_longitude = v.reported_longitude

                # Dynamically advance order statuses for active simulation realism
                ready_orders = db.scalars(
                    select(Order)
                    .where(Order.status.in_(["PAYMENT_CONFIRMED", "PROCESSING"]))
                    .where(Order.cyber_status != "UNDER_ATTACK")
                    .limit(2)
                ).all()
                for ro in ready_orders:
                    ro.status = "IN_TRANSIT"

                db.commit()
                await manager.broadcast({
                    "type": "FLEET_UPDATE",
                    "timestamp": datetime.utcnow().isoformat(),
                    "vehicles": [
                        {"id": v.id, "code": v.code, "latitude": v.reported_latitude, "longitude": v.reported_longitude, "status": v.status, "integrity": v.gps_integrity}
                        for v in vehicles
                    ]
                })

        except Exception as e:
            print(f"[LiveScanner] Error: {e}")
        finally:
            db.close()


async def _delayed_propagation(facility_id: int, label: str, confidence: float):
    """Waits 8 seconds then propagates the attack to remaining facility assets."""
    await asyncio.sleep(8)
    db = SessionLocal()
    try:
        AssetStateMachine(db).propagate_attack(facility_id, label, confidence)
        await manager.broadcast({
            "type": "PROPAGATION",
            "facility_id": facility_id,
            "label": label,
            "message": f"Lateral movement detected — {label} spreading through facility network.",
        })
    except Exception as e:
        print(f"[Propagation] Error: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    # Start the live ML scanner as a background task
    scanner_task = asyncio.create_task(live_scanner())
    yield
    scanner_task.cancel()


app = FastAPI(title="CyberSecureChain API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])



class TransitionRequest(BaseModel):
    target_state: str


class SimulationRequest(BaseModel):
    scenario: str = Field(pattern="^(ACCOUNT_COMPROMISE|INVENTORY_MANIPULATION|GPS_SPOOFING|QR_TAMPERING|SUPPLIER_COMPROMISE|IOT_SPOOFING|OT_DISRUPTION|RANSOMWARE_IMPACT)$")
    target_asset_id: int


class ResponseAction(BaseModel):
    action: str


def item_not_found():
    raise HTTPException(status_code=404, detail="Entity not found")


@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "synthetic-digital-twin"}


@app.get("/api/digital-twin")
def digital_twin(db: Session = Depends(get_db)):
    return DigitalTwinService(db).get_global_state()


@app.get("/api/digital-twin/map")
def twin_map(db: Session = Depends(get_db)):
    twin = DigitalTwinService(db)
    vehicles = db.scalars(select(Vehicle)).all()
    return {"facilities": twin.get_global_state()["facilities"], "relationships": twin.get_relationships(),
            "vehicles": [{"id": v.id, "code": v.code, "latitude": v.reported_latitude, "longitude": v.reported_longitude, "status": v.status, "integrity": v.gps_integrity} for v in vehicles]}


@app.get("/api/digital-twin/facility/{facility_id}")
def twin_facility(facility_id: int, db: Session = Depends(get_db)):
    try:
        return DigitalTwinService(db).get_facility_state(facility_id)
    except ValueError:
        item_not_found()


@app.get("/api/facilities")
def facilities(type: str | None = None, db: Session = Depends(get_db)):
    query = select(Facility)
    if type: query = query.where(Facility.type == type.upper())
    return DigitalTwinService(db).get_global_state()["facilities"] if not type else [DigitalTwinService(db)._facility(x) for x in db.scalars(query).all()]


@app.get("/api/facilities/{facility_id}")
def facility_detail(facility_id: int, db: Session = Depends(get_db)):
    try: return DigitalTwinService(db).get_facility_state(facility_id)
    except ValueError: item_not_found()


@app.get("/api/facilities/{facility_id}/activity")
def facility_activity(facility_id: int, db: Session = Depends(get_db)):
    facility = db.get(Facility, facility_id)
    if not facility: item_not_found()
    return DigitalTwinService(db).get_recent_events(50, facility.code)


@app.get("/api/inventory")
def inventory(facility_id: int | None = None, search: str | None = None, db: Session = Depends(get_db)):
    query = select(Inventory)
    if facility_id: query = query.where(Inventory.facility_id == facility_id)
    values = db.scalars(query).all()
    rows = [{"id": i.id, "sku": i.product.sku, "product": i.product.name, "category": i.product.category, "facility": i.facility.code,
             "batch": i.batch_code, "available": i.available, "reserved": i.reserved, "damaged": i.damaged, "quarantined": i.quarantined} for i in values]
    return [r for r in rows if not search or search.lower() in (r["sku"] + r["product"]).lower()]


@app.get("/api/inventory/{facility_id}")
def inventory_by_facility(facility_id: int, db: Session = Depends(get_db)):
    return inventory(facility_id, None, db)


@app.get("/api/products")
def products(search: str | None = None, db: Session = Depends(get_db)):
    values = db.scalars(select(Product)).all()
    rows = [{"id": p.id, "sku": p.sku, "name": p.name, "category": p.category, "supplier": p.supplier, "factory": p.factory, "price": p.price} for p in values]
    return [p for p in rows if not search or search.lower() in (p["sku"] + p["name"]).lower()]


@app.get("/api/products/{product_id}")
def product_detail(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: item_not_found()
    stock = db.scalars(select(Inventory).where(Inventory.product_id == product.id)).all()
    return {"id": product.id, "sku": product.sku, "name": product.name, "category": product.category, "supplier": product.supplier,
            "factory": product.factory, "inventory": [{"facility": i.facility.code, "available": i.available, "reserved": i.reserved, "batch": i.batch_code} for i in stock]}


@app.get("/api/orders")
def orders(limit: int = 100, db: Session = Depends(get_db)):
    values = db.scalars(select(Order).order_by(Order.id).limit(min(limit, 500))).all()
    shipments = {x.order_id: x for x in db.scalars(select(Shipment)).all()}
    return [{"id": o.id, "number": o.number, "customer": o.customer.name, "origin": o.origin.code, "destination": o.destination, "status": o.status,
             "shipment": shipments[o.id].code if o.id in shipments else None, "eta": o.eta, "cyber_status": o.cyber_status, "package": o.package_code} for o in values]


@app.get("/api/orders/{order_id}")
def order_detail(order_id: int, db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o: item_not_found()
    shipment = db.scalar(select(Shipment).where(Shipment.order_id == o.id))
    activity = [e for e in DigitalTwinService(db).get_recent_events(100, o.origin.code) if str(o.id) == e["id"] or o.number in e["description"]]
    return {"id": o.id, "number": o.number, "customer": o.customer.name, "origin": o.origin.code, "destination": o.destination, "status": o.status,
            "cyber_status": o.cyber_status, "eta": o.eta, "package": {"code": o.package_code, "integrity": "VERIFIED", "chain_of_custody": ["Factory", "Quality Check", "FC-JPR-01", "Picking", "Packing", "Truck"]},
            "shipment": None if not shipment else {"code": shipment.code, "status": shipment.status, "vehicle": shipment.vehicle.code, "driver": shipment.vehicle.driver}, "timeline": activity}


@app.post("/api/orders/{order_id}/transition")
def transition_order(order_id: int, request: TransitionRequest, db: Session = Depends(get_db)):
    try:
        order = OperationsService.transition_order(db, order_id, request.target_state)
        db.commit(); return {"id": order.id, "status": order.status}
    except ValueError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail=str(exc))


@app.get("/api/shipments")
def shipments(db: Session = Depends(get_db)):
    values = db.scalars(select(Shipment).order_by(Shipment.id).limit(250)).all()
    return [{"id": s.id, "code": s.code, "order": s.order.number, "origin": s.origin, "destination": s.destination, "vehicle": s.vehicle.code, "driver": s.vehicle.driver, "status": s.status, "eta": s.eta, "package_count": s.package_count, "integrity": s.integrity} for s in values]


@app.get("/api/shipments/{shipment_id}")
def shipment_detail(shipment_id: int, db: Session = Depends(get_db)):
    s = db.get(Shipment, shipment_id)
    if not s: item_not_found()
    return {"id": s.id, "code": s.code, "order": s.order.number, "origin": s.origin, "destination": s.destination, "status": s.status, "eta": s.eta,
            "integrity": s.integrity, "vehicle": {"code": s.vehicle.code, "driver": s.vehicle.driver, "latitude": s.vehicle.reported_latitude, "longitude": s.vehicle.reported_longitude, "gps_integrity": s.vehicle.gps_integrity}}


@app.get("/api/vehicles")
def vehicles(db: Session = Depends(get_db)):
    return [{"id": v.id, "code": v.code, "driver": v.driver, "status": v.status, "latitude": v.reported_latitude, "longitude": v.reported_longitude,
             "actual_latitude": v.current_latitude, "actual_longitude": v.current_longitude, "destination": v.destination, "gps_integrity": v.gps_integrity} for v in db.scalars(select(Vehicle)).all()]


@app.get("/api/employees")
def employees(db: Session = Depends(get_db)):
    return [{"id": e.id, "code": e.employee_code, "name": e.name, "facility": e.facility.code, "role": e.role, "username": e.username,
             "mfa": "ENABLED" if e.mfa_enabled else "DISABLED", "account_status": e.account_status, "last_login": e.last_login} for e in db.scalars(select(Employee)).all()]


def operational_assets(asset_type: str, db: Session):
    return operational_assets_for_types({asset_type}, db)


def operational_assets_for_types(asset_types: set[str], db: Session):
    return [{"id": a.id, "code": a.asset_code, "name": a.name, "type": a.asset_type, "facility": a.facility.code, "zone": a.zone,
             "status": a.status, "criticality": a.criticality, "firmware": a.firmware, "network": a.network, "cyber_status": a.cyber_status} for a in db.scalars(select(OperationalAsset).where(OperationalAsset.asset_type.in_(asset_types))).all()]


@app.get("/api/machines")
def machines(db: Session = Depends(get_db)): return operational_assets_for_types({"MACHINE", "ROBOT"}, db)


@app.get("/api/robots")
def robots(db: Session = Depends(get_db)): return operational_assets("ROBOT", db)


@app.get("/api/iot")
def iot(db: Session = Depends(get_db)): return operational_assets_for_types({"IOT", "OT"}, db)


@app.get("/api/ot")
def ot(db: Session = Depends(get_db)): return operational_assets("OT", db)


@app.get("/api/operational-assets")
def all_operational_assets(types: str | None = None, db: Session = Depends(get_db)):
    requested_types = {value.strip().upper() for value in types.split(",")} if types else None
    values = db.scalars(select(OperationalAsset)).all()
    return [{"id": asset.id, "code": asset.asset_code, "name": asset.name, "type": asset.asset_type,
             "facility": asset.facility.code, "zone": asset.zone, "status": asset.status,
             "criticality": asset.criticality, "firmware": asset.firmware, "network": asset.network,
             "cyber_status": asset.cyber_status} for asset in values if not requested_types or asset.asset_type in requested_types]


@app.get("/api/events")
def events(category: str | None = None, db: Session = Depends(get_db)):
    items = DigitalTwinService(db).get_recent_events(100)
    return [e for e in items if not category or e["category"] == category.upper()]


@app.get("/api/cyber/overview")
def cyber_overview(db: Session = Depends(get_db)):
    state = DigitalTwinService(db).get_cyber_state()
    state["active_incidents"] = db.scalar(select(func.count()).select_from(Incident).where(Incident.status != "RECOVERED")) or 0
    state["external_connections"] = sum(a["type"] == "CONNECTION" for a in state["assets"])
    return state


@app.get("/api/cyber/assets")
@app.get("/api/cyber/attack-surface")
def cyber_assets(db: Session = Depends(get_db)):
    return [asset_payload(a) for a in db.scalars(select(CyberAsset)).all()]


@app.get("/api/cyber/assets/{asset_id}")
def cyber_asset_detail(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(CyberAsset, asset_id)
    if not asset: item_not_found()
    return asset_payload(asset)


@app.get("/api/cyber/risk")
def risk(db: Session = Depends(get_db)):
    return DigitalTwinService(db).get_cyber_state()["assets"]


@app.get("/api/cyber/vulnerabilities")
def vulnerabilities(db: Session = Depends(get_db)):
    return [{"asset": a.asset_code, "asset_name": a.name, "facility": a.facility.code if a.facility else "External", "vulnerability": v,
             "severity": asset_payload(a)["risk_level"], "recommended_control": ", ".join(a.controls)} for a in db.scalars(select(CyberAsset)).all() for v in a.vulnerabilities]


@app.get("/api/cyber/incidents")
def incidents(db: Session = Depends(get_db)):
    return [{"id": i.id, "code": i.code, "severity": i.severity, "status": i.status, "facility": i.facility_code, "summary": i.summary, "actions": i.actions} for i in db.scalars(select(Incident)).all()]


@app.get("/api/cyber/attack-path/{asset_id}")
def attack_path(asset_id: int, db: Session = Depends(get_db)):
    source = db.get(CyberAsset, asset_id)
    if not source: item_not_found()
    peers = db.scalars(select(CyberAsset).where(CyberAsset.facility_id == source.facility_id, CyberAsset.id != source.id)).all()
    return {"source": asset_payload(source), "nodes": [asset_payload(source), *[asset_payload(a) for a in peers]],
            "edges": [{"source": source.asset_code, "target": a.asset_code, "relationship": "CONNECTS_TO", "reason": "Shared modeled facility dependency"} for a in peers]}


@app.get("/api/cyber/controls")
def controls(db: Session = Depends(get_db)):
    return [{"id": c.id, "code": c.code, "name": c.name, "description": c.description, "enabled": c.enabled} for c in db.scalars(select(SecurityControl)).all()]


@app.post("/api/cyber/controls/{control_id}/toggle")
def toggle_control(control_id: int, db: Session = Depends(get_db)):
    control = db.get(SecurityControl, control_id)
    if not control: item_not_found()
    control.enabled = not control.enabled; db.commit()
    return {"id": control.id, "enabled": control.enabled}


@app.post("/api/simulations")
def create_simulation(request: SimulationRequest, db: Session = Depends(get_db)):
    try:
        simulation = SimulationEngine(db).launch(request.scenario, request.target_asset_id)
        db.commit(); return {"id": simulation.id, "status": simulation.status, "scenario": simulation.scenario}
    except ValueError as exc:
        db.rollback(); raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/simulations/{simulation_id}/start")
def start_simulation(simulation_id: int, db: Session = Depends(get_db)):
    try:
        simulation = SimulationEngine(db).start(simulation_id)
        db.commit(); return {"id": simulation.id, "status": simulation.status, "result": simulation.result}
    except ValueError as exc:
        db.rollback(); raise HTTPException(status_code=409, detail=str(exc))


@app.post("/api/simulations/automatic-attack")
def automatic_attack(db: Session = Depends(get_db)):
    try:
        simulation = SimulationEngine(db).automatic_attack()
        db.commit()
        return {"id": simulation.id, "status": simulation.status, "scenario": simulation.scenario, "result": simulation.result}
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc))


@app.get("/api/simulations/{simulation_id}")
def simulation(simulation_id: int, db: Session = Depends(get_db)):
    value = db.get(Simulation, simulation_id)
    if not value: item_not_found()
    return {"id": value.id, "scenario": value.scenario, "status": value.status, "snapshot": value.snapshot, "result": value.result}


@app.get("/api/cyber/what-if")
def what_if(scenario: str = "ACCOUNT_COMPROMISE", target_asset_id: int = 1, db: Session = Depends(get_db)):
    try:
        return SimulationEngine(db).compare(scenario, target_asset_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@app.post("/api/incidents/{incident_id}/respond")
def incident_response(incident_id: int, request: ResponseAction, db: Session = Depends(get_db)):
    try:
        incident = SimulationEngine(db).respond(incident_id, request.action)
        db.commit(); return {"id": incident.id, "status": incident.status, "actions": incident.actions}
    except ValueError as exc:
        db.rollback(); raise HTTPException(status_code=404, detail=str(exc))


@app.websocket("/ws/live")
async def live_socket(ws: WebSocket):
    """Real-time WebSocket feed — streams every ML traffic detection event."""
    await manager.connect(ws)
    try:
        # Send a welcome handshake immediately
        await ws.send_json({
            "type": "CONNECTED",
            "message": "Live IDS ML stream connected. Monitoring all facilities.",
        })
        while True:
            # Keep connection alive — client sends pings
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.websocket("/ws/events")
async def event_socket(ws: WebSocket):
    """Legacy endpoint — redirects to /ws/live for backward compatibility."""
    await manager.connect(ws)
    try:
        await ws.send_json({"type": "HEARTBEAT", "message": "Digital twin event stream connected"})
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


class InjectAttackRequest(BaseModel):
    scenario: str
    facility_code: str
    duration_seconds: float = 60.0


@app.post("/api/live/inject")
def inject_live_attack(request: InjectAttackRequest, db: Session = Depends(get_db)):
    """
    Inject a live attack into the traffic generator for a specific facility.
    This makes the ML model start seeing malicious packets from that facility,
    triggering real-time detections, state changes, and WebSocket alerts.
    """
    facility = db.scalar(select(Facility).where(Facility.code == request.facility_code))
    if not facility:
        raise HTTPException(status_code=404, detail=f"Facility {request.facility_code} not found")
    traffic_gen.inject_attack(request.facility_code, request.scenario, request.duration_seconds)
    return {
        "status": "INJECTED",
        "facility_code": request.facility_code,
        "scenario": request.scenario,
        "duration_seconds": request.duration_seconds,
        "message": f"Attack injection active. ML scanner will detect within ~3 seconds.",
    }


@app.delete("/api/live/inject/{facility_code}")
def clear_live_attack(facility_code: str, db: Session = Depends(get_db)):
    """Stop injecting attack traffic for a facility, allowing recovery."""
    traffic_gen.clear_attack(facility_code)
    return {"status": "CLEARED", "facility_code": facility_code}


@app.get("/api/live/status")
def live_status():
    """Return the current live attack injection status for all facilities."""
    attacks = traffic_gen.active_attacks()
    return {
        "connected_clients": len(manager.active),
        "active_attacks": attacks,
        "scanner_running": True,
    }


# ---------------------------------------------------------------------------
# Autonomous Red vs Blue Cyber Engine Endpoints
# ---------------------------------------------------------------------------

class SpeedRequest(BaseModel):
    speed: str


@app.get("/api/cyber/auto-defense/status")
def get_auto_defense_status():
    """Return autonomous adversary & SOAR status, metrics, and active campaign."""
    return autonomous_engine.get_status()


@app.post("/api/cyber/auto-defense/toggle-adversary")
def toggle_auto_adversary():
    """Toggle autonomous adversary (Red Team AI)."""
    autonomous_engine.adversary_enabled = not autonomous_engine.adversary_enabled
    return {"adversary_enabled": autonomous_engine.adversary_enabled}


@app.post("/api/cyber/auto-defense/toggle-mitigation")
def toggle_auto_mitigation():
    """Toggle autonomous SOAR mitigation (Blue Team AI)."""
    autonomous_engine.mitigation_enabled = not autonomous_engine.mitigation_enabled
    return {"mitigation_enabled": autonomous_engine.mitigation_enabled}


@app.post("/api/cyber/auto-defense/set-speed")
def set_auto_defense_speed(request: SpeedRequest):
    """Set autonomous cycle speed ('fast', 'normal', 'relaxed')."""
    if request.speed in ("fast", "normal", "relaxed"):
        autonomous_engine.speed = request.speed
    return {"speed": autonomous_engine.speed}


@app.post("/api/cyber/auto-defense/trigger-campaign")
async def trigger_auto_campaign(db: Session = Depends(get_db)):
    """Manually force the adversary AI to launch an attack campaign immediately."""
    camp = await autonomous_engine.launch_campaign(db, traffic_gen, manager.broadcast)
    return {"status": "LAUNCHED", "campaign": camp}


@app.post("/api/cyber/auto-defense/trigger-defense")
async def trigger_auto_defense(db: Session = Depends(get_db)):
    """Manually trigger the SOAR auto-defender to execute mitigation playbooks."""
    await autonomous_engine.execute_soar_defense(db, traffic_gen, manager.broadcast)
    return {"status": "MITIGATED", "status_data": autonomous_engine.get_status()}


@app.get("/api/cyber/live-packets")
def get_live_packets():
    """Return recently scanned network packets with full CIC-IDS2017 metrics for the visual HUD."""
    return traffic_gen.get_recent_packets()


