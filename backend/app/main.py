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
from app.models import (
    CyberAsset, Employee, Event, Facility, Incident, Inventory, OperationalAsset,
    Order, Product, SecurityControl, Shipment, Simulation, Vehicle,
    # SupplyLens AI models
    Supplier, SoftwareProject, SbomImportJob, SoftwareComponent,
    ComponentDependency, ComponentFinding, ComponentDeployment,
    MitigationAction, RiskSnapshot,
)
from app.seed import seed
from app.seed_supplylens import seed_supplylens
from app.services.operations import OperationsService
from app.services.supplylens_sbom import detect_sbom_format, parse_cyclonedx_json, parse_spdx_json, SbomValidationError, MAX_SBOM_BYTES
from app.services.supplylens_risk import calculate_risk, get_risk_band
from app.services.supplylens_enrichment import VulnerabilityEnrichmentService
from app.services.supplylens_copilot import RiskCopilotService
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

            # 1.5 Auto-mitigate expired campaigns (only once, when traffic expires)
            if autonomous_engine.current_campaign:
                stage = autonomous_engine.current_campaign.get("stage")
                if stage in ("ATTACK_IN_PROGRESS", "ML_IDS_DETECTED"):
                    active_attacks = traffic_gen.active_attacks()
                    camp_fac = autonomous_engine.current_campaign.get("facility_code")
                    if camp_fac not in active_attacks:
                        # Attack traffic has expired — trigger SOAR once
                        await autonomous_engine.execute_soar_defense(db, traffic_gen, manager.broadcast)

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
        seed_supplylens(db)
    finally:
        db.close()
    # Start the live ML scanner as a background task
    scanner_task = asyncio.create_task(live_scanner())
    yield
    scanner_task.cancel()



app = FastAPI(title="CyberSecureChain API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Global exception handler — always injects CORS headers even on crashes
# This ensures the browser can read 500 error responses from cross-origin
# ---------------------------------------------------------------------------
from fastapi.responses import JSONResponse
from fastapi import Request as FastAPIRequest


@app.exception_handler(Exception)
async def global_exception_handler(request: FastAPIRequest, exc: Exception):
    origin = request.headers.get("origin", "")
    cors_headers = {}
    # Match vercel.app origins or explicit allowed origins
    import re
    if origin and (re.match(r"https://.*\.vercel\.app", origin) or origin in settings.cors_origins):
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=cors_headers,
    )



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


class CampaignRequest(BaseModel):
    scenario: Optional[str] = None

@app.post("/api/cyber/auto-defense/trigger-campaign")
async def trigger_auto_campaign(req: Optional[CampaignRequest] = None, db: Session = Depends(get_db)):
    """Manually force the adversary AI to launch an attack campaign immediately."""
    scenario = req.scenario if req else None
    camp = await autonomous_engine.launch_campaign(db, traffic_gen, manager.broadcast, forced_scenario=scenario)
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



# ===========================================================================
# SupplyLens AI — Software & Supplier Risk Intelligence API
# ===========================================================================

class CreateProjectRequest(BaseModel):
    code: str
    name: str
    description: str = ""
    version: str = "1.0.0"
    business_owner: str = ""
    criticality: int = 5
    repository_url: Optional[str] = None
    facility_id: Optional[int] = None


class ImportSbomRequest(BaseModel):
    filename: str
    content: str  # raw JSON string


class CreateSupplierRequest(BaseModel):
    code: str
    name: str
    category: str = "SOFTWARE"
    description: str = ""
    business_owner: str = ""
    criticality: int = 5
    tier: str = "TIER_1"
    contact_email: str = ""
    data_sensitivity: str = "MEDIUM"
    notes: Optional[str] = None
    assessment_status: str = "PENDING_REVIEW"


class UpdateSupplierRequest(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    business_owner: Optional[str] = None
    criticality: Optional[int] = None
    tier: Optional[str] = None
    contact_email: Optional[str] = None
    data_sensitivity: Optional[str] = None
    notes: Optional[str] = None
    assessment_status: Optional[str] = None
    last_assessment_date: Optional[str] = None
    evidence_url: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None


class FindingStatusRequest(BaseModel):
    status: str  # OPEN, IN_TRIAGE, MITIGATED, ACCEPTED


class CreateDeploymentRequest(BaseModel):
    component_id: int
    service_name: str
    cyber_asset_id: Optional[int] = None
    operational_asset_id: Optional[int] = None
    facility_id: Optional[int] = None
    business_process: str = "Fulfillment Operations"
    mapping_type: str = "USER_MAPPED"
    notes: Optional[str] = None


class CopilotQueryRequest(BaseModel):
    prompt: str
    project_id: Optional[int] = None


class CreateMitigationRequest(BaseModel):
    finding_id: Optional[int] = None
    component_id: Optional[int] = None
    supplier_id: Optional[int] = None
    title: str
    action_type: str
    notes: Optional[str] = None


class MitigationStatusRequest(BaseModel):
    status: str


@app.get("/api/supplylens/overview")
def supplylens_overview(db: Session = Depends(get_db)):
    """High-level SupplyLens metrics summary."""
    from sqlalchemy import func as sa_func
    projects = db.scalar(select(sa_func.count(SoftwareProject.id))) or 0
    components = db.scalar(select(sa_func.count(SoftwareComponent.id))) or 0
    suppliers = db.scalar(select(sa_func.count(Supplier.id))) or 0
    findings = db.scalar(select(sa_func.count(ComponentFinding.id))) or 0
    critical_findings = db.scalar(
        select(sa_func.count(ComponentFinding.id)).where(ComponentFinding.severity == "CRITICAL")
    ) or 0
    high_findings = db.scalar(
        select(sa_func.count(ComponentFinding.id)).where(ComponentFinding.severity == "HIGH")
    ) or 0
    kev_findings = db.scalar(
        select(sa_func.count(ComponentFinding.id)).where(ComponentFinding.cisa_kev == True)
    ) or 0
    open_findings = db.scalar(
        select(sa_func.count(ComponentFinding.id)).where(ComponentFinding.status == "OPEN")
    ) or 0
    deployments = db.scalar(select(sa_func.count(ComponentDeployment.id))) or 0
    mitigations = db.scalar(select(sa_func.count(MitigationAction.id))) or 0
    avg_risk_row = db.scalar(select(sa_func.avg(SoftwareComponent.risk_score)))
    avg_risk = round(float(avg_risk_row), 1) if avg_risk_row else 0.0
    recent_findings = db.scalars(
        select(ComponentFinding)
        .order_by(ComponentFinding.created_at.desc()).limit(5)
    ).all()
    recent_list = [
        {
            "id": f.id, "vulnerability_id": f.vulnerability_id,
            "severity": f.severity, "status": f.status,
            "cisa_kev": f.cisa_kev, "summary": f.summary[:100] if f.summary else ""
        }
        for f in recent_findings
    ]
    return {
        "projects": projects,
        "components": components,
        "suppliers": suppliers,
        "findings": findings,
        "open_findings": open_findings,
        "critical_findings": critical_findings,
        "high_findings": high_findings,
        "kev_findings": kev_findings,
        "cyber_physical_mappings": deployments,
        "mitigations": mitigations,
        "average_component_risk": avg_risk,
        "recent_findings": recent_list,
        "data_label": "SYNTHETIC_DEMO",
    }


@app.get("/api/supplylens/projects")
def list_projects(db: Session = Depends(get_db)):
    rows = db.scalars(select(SoftwareProject).order_by(SoftwareProject.name)).all()
    result = []
    for p in rows:
        component_count = db.scalar(
            select(select(SoftwareComponent.id).where(SoftwareComponent.project_id == p.id).subquery().c.id.count())
        ) or len(p.components)
        result.append({
            "id": p.id, "code": p.code, "name": p.name,
            "description": p.description, "version": p.version,
            "business_owner": p.business_owner, "criticality": p.criticality,
            "component_count": len(p.components),
            "facility": p.facility.code if p.facility else None,
            "created_at": p.created_at.isoformat(),
        })
    return result


@app.post("/api/supplylens/projects", status_code=201)
def create_project(req: CreateProjectRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(SoftwareProject).where(SoftwareProject.code == req.code))
    if existing:
        raise HTTPException(status_code=409, detail=f"Project code '{req.code}' already exists")
    project = SoftwareProject(
        code=req.code, name=req.name, description=req.description,
        version=req.version, business_owner=req.business_owner,
        criticality=req.criticality, repository_url=req.repository_url,
        facility_id=req.facility_id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return {"id": project.id, "code": project.code, "name": project.name}


@app.get("/api/supplylens/projects/{project_id}")
def project_detail(project_id: int, db: Session = Depends(get_db)):
    project = db.get(SoftwareProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    components = [
        {
            "id": c.id, "name": c.name, "version": c.version,
            "ecosystem": c.ecosystem, "risk_score": c.risk_score,
            "risk_level": c.risk_level, "direct": c.direct,
            "finding_count": len(c.findings),
        }
        for c in project.components
    ]
    import_jobs = [
        {
            "id": j.id, "filename": j.filename, "format": j.format,
            "status": j.status, "component_count": j.component_count,
            "created_at": j.created_at.isoformat(),
        }
        for j in project.import_jobs
    ]
    return {
        "id": project.id, "code": project.code, "name": project.name,
        "description": project.description, "version": project.version,
        "business_owner": project.business_owner, "criticality": project.criticality,
        "repository_url": project.repository_url,
        "facility": project.facility.code if project.facility else None,
        "components": components,
        "import_jobs": import_jobs,
        "created_at": project.created_at.isoformat(),
    }


@app.post("/api/supplylens/projects/{project_id}/import-sbom")
def import_sbom(project_id: int, req: ImportSbomRequest, db: Session = Depends(get_db)):
    """Parse and import an SBOM (CycloneDX or SPDX JSON) into the project."""
    project = db.get(SoftwareProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if len(req.content) > MAX_SBOM_BYTES:
        raise HTTPException(status_code=413, detail=f"SBOM too large (max {MAX_SBOM_BYTES // 1024}KB)")
    try:
        import json as _json
        sbom_data = _json.loads(req.content)
    except Exception:
        raise HTTPException(status_code=422, detail="Invalid JSON content")
    try:
        fmt = detect_sbom_format(sbom_data)
    except SbomValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    job = SbomImportJob(
        project_id=project_id, filename=req.filename,
        format=fmt, status="PROCESSING"
    )
    db.add(job)
    db.flush()
    try:
        if fmt == "CYCLONEDX_JSON":
            components, deps, warnings = parse_cyclonedx_json(sbom_data)
        else:
            components, deps, warnings = parse_spdx_json(sbom_data)
        added = 0
        for comp_data in components:
            comp = SoftwareComponent(
                project_id=project_id,
                name=comp_data.get("name", "unknown"),
                version=comp_data.get("version", "0.0.0"),
                ecosystem=comp_data.get("ecosystem", "generic"),
                purl=comp_data.get("purl"),
                license=comp_data.get("license"),
                direct=comp_data.get("direct", True),
                scope=comp_data.get("scope", "runtime"),
                raw_metadata=comp_data,
            )
            db.add(comp)
            added += 1
        job.component_count = added
        job.relationship_count = len(deps)
        job.warnings = warnings
        job.status = "COMPLETED"
        db.commit()
        return {
            "job_id": job.id, "format": fmt, "status": "COMPLETED",
            "components_added": added, "relationships": len(deps),
            "warnings": warnings,
        }
    except Exception as exc:
        job.status = "FAILED"
        job.error_message = str(exc)
        db.commit()
        raise HTTPException(status_code=422, detail=f"Parse failed: {exc}")


@app.get("/api/supplylens/imports")
def list_imports(db: Session = Depends(get_db)):
    jobs = db.scalars(select(SbomImportJob).order_by(SbomImportJob.created_at.desc())).all()
    return [
        {
            "id": j.id, "project_id": j.project_id,
            "project_name": j.project.name if j.project else None,
            "filename": j.filename, "format": j.format, "status": j.status,
            "component_count": j.component_count, "relationship_count": j.relationship_count,
            "created_at": j.created_at.isoformat(),
        }
        for j in jobs
    ]


@app.get("/api/supplylens/imports/{job_id}")
def import_detail(job_id: int, db: Session = Depends(get_db)):
    job = db.get(SbomImportJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Import job not found")
    return {
        "id": job.id, "project_id": job.project_id,
        "filename": job.filename, "format": job.format, "status": job.status,
        "component_count": job.component_count, "relationship_count": job.relationship_count,
        "warnings": job.warnings, "error_message": job.error_message,
        "created_at": job.created_at.isoformat(),
    }


@app.get("/api/supplylens/components")
def list_components(
    project_id: Optional[int] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = select(SoftwareComponent)
    if project_id:
        query = query.where(SoftwareComponent.project_id == project_id)
    if search:
        query = query.where(SoftwareComponent.name.ilike(f"%{search}%"))
    components = db.scalars(query.order_by(SoftwareComponent.risk_score.desc())).all()
    result = []
    for c in components:
        finding_count = len(c.findings)
        if severity:
            filtered = [f for f in c.findings if f.severity == severity]
            if not filtered:
                continue
            finding_count = len(filtered)
        result.append({
            "id": c.id, "name": c.name, "version": c.version,
            "ecosystem": c.ecosystem, "purl": c.purl, "license": c.license,
            "direct": c.direct, "scope": c.scope,
            "risk_score": c.risk_score, "risk_level": c.risk_level,
            "finding_count": finding_count,
            "project_id": c.project_id,
            "supplier_id": c.supplier_id,
            "supplier_name": c.supplier.name if c.supplier else None,
            "deployment_count": len(c.deployments),
            "created_at": c.created_at.isoformat(),
        })
    return result


@app.get("/api/supplylens/components/{component_id}")
def component_detail(component_id: int, db: Session = Depends(get_db)):
    comp = db.get(SoftwareComponent, component_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    findings = [
        {
            "id": f.id, "vulnerability_id": f.vulnerability_id,
            "source": f.source, "severity": f.severity, "cvss_score": f.cvss_score,
            "cisa_kev": f.cisa_kev, "summary": f.summary, "status": f.status,
            "fixed_version": f.fixed_version, "risk_score": f.risk_score,
            "confidence": f.confidence, "created_at": f.created_at.isoformat(),
        }
        for f in comp.findings
    ]
    deployments = [
        {
            "id": d.id, "service_name": d.service_name,
            "business_process": d.business_process, "mapping_type": d.mapping_type,
            "facility": d.facility.code if d.facility else None,
            "cyber_asset": d.cyber_asset.code if d.cyber_asset else None,
            "created_at": d.created_at.isoformat(),
        }
        for d in comp.deployments
    ]
    return {
        "id": comp.id, "name": comp.name, "version": comp.version,
        "ecosystem": comp.ecosystem, "purl": comp.purl, "license": comp.license,
        "direct": comp.direct, "scope": comp.scope,
        "risk_score": comp.risk_score, "risk_level": comp.risk_level,
        "project_id": comp.project_id,
        "supplier": {"id": comp.supplier.id, "name": comp.supplier.name} if comp.supplier else None,
        "findings": findings,
        "deployments": deployments,
        "raw_metadata": comp.raw_metadata,
        "created_at": comp.created_at.isoformat(),
    }


@app.get("/api/supplylens/components/{component_id}/graph")
def component_graph(component_id: int, db: Session = Depends(get_db)):
    """Return dependency graph edges for a component (and siblings in same project)."""
    comp = db.get(SoftwareComponent, component_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    edges = db.scalars(
        select(ComponentDependency).where(
            (ComponentDependency.project_id == comp.project_id) &
            ((ComponentDependency.parent_id == component_id) | (ComponentDependency.child_id == component_id))
        )
    ).all()
    nodes_ids = set()
    edge_list = []
    for e in edges:
        nodes_ids.add(e.parent_id)
        nodes_ids.add(e.child_id)
        edge_list.append({"parent_id": e.parent_id, "child_id": e.child_id, "type": e.relationship_type})
    nodes = []
    for nid in nodes_ids:
        n = db.get(SoftwareComponent, nid)
        if n:
            nodes.append({"id": n.id, "name": n.name, "version": n.version,
                          "risk_level": n.risk_level, "risk_score": n.risk_score})
    return {"nodes": nodes, "edges": edge_list}


@app.post("/api/supplylens/components/{component_id}/enrich")
async def enrich_component(component_id: int, db: Session = Depends(get_db)):
    """Trigger OSV.dev enrichment for a component and store results."""
    comp = db.get(SoftwareComponent, component_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    svc = VulnerabilityEnrichmentService()
    results = await svc.enrich_component(comp.ecosystem, comp.name, comp.version)
    added = 0
    for r in results:
        existing = db.scalar(
            select(ComponentFinding).where(
                ComponentFinding.component_id == component_id,
                ComponentFinding.vulnerability_id == r["vulnerability_id"]
            )
        )
        if not existing:
            finding = ComponentFinding(
                component_id=component_id,
                vulnerability_id=r["vulnerability_id"],
                source=r.get("source", "OSV"),
                severity=r.get("severity", "MEDIUM"),
                cvss_score=r.get("cvss_score"),
                cisa_kev=r.get("cisa_kev", False),
                summary=r.get("summary", ""),
                details=r.get("details", ""),
                fixed_version=r.get("fixed_version"),
                confidence=r.get("confidence", "LIVE_OSV"),
                evidence=r,
            )
            db.add(finding)
            added += 1
    db.commit()
    return {"enriched": True, "new_findings": added, "total_from_source": len(results)}


@app.get("/api/supplylens/findings")
def list_findings(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    cisa_kev: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = select(ComponentFinding)
    if severity:
        query = query.where(ComponentFinding.severity == severity)
    if status:
        query = query.where(ComponentFinding.status == status)
    if cisa_kev is not None:
        query = query.where(ComponentFinding.cisa_kev == cisa_kev)
    findings = db.scalars(query.order_by(ComponentFinding.risk_score.desc(), ComponentFinding.created_at.desc())).all()
    return [
        {
            "id": f.id, "component_id": f.component_id,
            "component_name": f.component.name if f.component else None,
            "vulnerability_id": f.vulnerability_id, "source": f.source,
            "severity": f.severity, "cvss_score": f.cvss_score,
            "cisa_kev": f.cisa_kev, "summary": f.summary[:160] if f.summary else "",
            "status": f.status, "fixed_version": f.fixed_version,
            "risk_score": f.risk_score, "confidence": f.confidence,
            "created_at": f.created_at.isoformat(),
        }
        for f in findings
    ]


@app.get("/api/supplylens/findings/{finding_id}")
def finding_detail(finding_id: int, db: Session = Depends(get_db)):
    f = db.get(ComponentFinding, finding_id)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    return {
        "id": f.id, "component_id": f.component_id,
        "component_name": f.component.name if f.component else None,
        "vulnerability_id": f.vulnerability_id, "source": f.source,
        "severity": f.severity, "cvss_score": f.cvss_score,
        "cisa_kev": f.cisa_kev, "summary": f.summary, "details": f.details,
        "affected_versions": f.affected_versions, "fixed_version": f.fixed_version,
        "status": f.status, "risk_score": f.risk_score, "confidence": f.confidence,
        "evidence": f.evidence, "created_at": f.created_at.isoformat(),
        "mitigations": [
            {"id": m.id, "title": m.title, "action_type": m.action_type, "status": m.status}
            for m in f.mitigations
        ],
    }


@app.patch("/api/supplylens/findings/{finding_id}/status")
def update_finding_status(finding_id: int, req: FindingStatusRequest, db: Session = Depends(get_db)):
    f = db.get(ComponentFinding, finding_id)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
    valid_statuses = {"OPEN", "IN_TRIAGE", "MITIGATED", "ACCEPTED"}
    if req.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Status must be one of: {', '.join(valid_statuses)}")
    f.status = req.status
    db.commit()
    return {"id": f.id, "status": f.status}


@app.get("/api/supplylens/suppliers")
def list_suppliers(db: Session = Depends(get_db)):
    suppliers = db.scalars(select(Supplier).order_by(Supplier.risk_score.desc())).all()
    return [
        {
            "id": s.id, "code": s.code, "name": s.name, "category": s.category,
            "tier": s.tier, "criticality": s.criticality,
            "assessment_status": s.assessment_status,
            "risk_score": s.risk_score, "risk_level": s.risk_level,
            "component_count": len(s.components),
            "data_sensitivity": s.data_sensitivity,
            "contact_email": s.contact_email,
            "last_assessment_date": s.last_assessment_date,
            "created_at": s.created_at.isoformat(),
        }
        for s in suppliers
    ]


@app.post("/api/supplylens/suppliers", status_code=201)
def create_supplier(req: CreateSupplierRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(Supplier).where(Supplier.code == req.code))
    if existing:
        raise HTTPException(status_code=409, detail=f"Supplier code '{req.code}' already exists")
    supplier = Supplier(
        code=req.code, name=req.name, category=req.category,
        description=req.description, business_owner=req.business_owner,
        criticality=req.criticality, tier=req.tier,
        contact_email=req.contact_email, data_sensitivity=req.data_sensitivity,
        notes=req.notes, assessment_status=req.assessment_status,
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return {"id": supplier.id, "code": supplier.code, "name": supplier.name}


@app.get("/api/supplylens/suppliers/{supplier_id}")
def supplier_detail(supplier_id: int, db: Session = Depends(get_db)):
    s = db.get(Supplier, supplier_id)
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {
        "id": s.id, "code": s.code, "name": s.name, "category": s.category,
        "description": s.description, "business_owner": s.business_owner,
        "tier": s.tier, "criticality": s.criticality,
        "assessment_status": s.assessment_status,
        "contact_email": s.contact_email,
        "last_assessment_date": s.last_assessment_date,
        "evidence_url": s.evidence_url,
        "data_sensitivity": s.data_sensitivity,
        "risk_score": s.risk_score, "risk_level": s.risk_level,
        "notes": s.notes,
        "components": [
            {"id": c.id, "name": c.name, "version": c.version, "ecosystem": c.ecosystem}
            for c in s.components
        ],
        "created_at": s.created_at.isoformat(),
    }


@app.put("/api/supplylens/suppliers/{supplier_id}")
def update_supplier(supplier_id: int, req: UpdateSupplierRequest, db: Session = Depends(get_db)):
    s = db.get(Supplier, supplier_id)
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    fields = req.model_dump(exclude_none=True)
    for k, v in fields.items():
        setattr(s, k, v)
    db.commit()
    return {"id": s.id, "code": s.code, "name": s.name, "assessment_status": s.assessment_status}


@app.delete("/api/supplylens/suppliers/{supplier_id}")
def delete_supplier(supplier_id: int, confirm: bool = False, db: Session = Depends(get_db)):
    if not confirm:
        raise HTTPException(status_code=400, detail="Pass ?confirm=true to delete a supplier")
    s = db.get(Supplier, supplier_id)
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    if s.components:
        raise HTTPException(status_code=409, detail="Supplier has linked components; unlink them first")
    db.delete(s)
    db.commit()
    return {"deleted": supplier_id}


@app.get("/api/supplylens/deployments")
def list_deployments(db: Session = Depends(get_db)):
    deps = db.scalars(select(ComponentDeployment).order_by(ComponentDeployment.created_at.desc())).all()
    return [
        {
            "id": d.id, "component_id": d.component_id,
            "component_name": d.component.name if d.component else None,
            "service_name": d.service_name, "business_process": d.business_process,
            "mapping_type": d.mapping_type,
            "facility": d.facility.code if d.facility else None,
            "facility_id": d.facility_id,
            "cyber_asset": d.cyber_asset.code if d.cyber_asset else None,
            "cyber_asset_id": d.cyber_asset_id,
            "notes": d.notes, "created_at": d.created_at.isoformat(),
        }
        for d in deps
    ]


@app.post("/api/supplylens/deployments", status_code=201)
def create_deployment(req: CreateDeploymentRequest, db: Session = Depends(get_db)):
    comp = db.get(SoftwareComponent, req.component_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Component not found")
    dep = ComponentDeployment(
        component_id=req.component_id, service_name=req.service_name,
        cyber_asset_id=req.cyber_asset_id, operational_asset_id=req.operational_asset_id,
        facility_id=req.facility_id, business_process=req.business_process,
        mapping_type=req.mapping_type, notes=req.notes,
    )
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return {"id": dep.id, "component_id": dep.component_id, "service_name": dep.service_name}


@app.delete("/api/supplylens/deployments/{deployment_id}")
def delete_deployment(deployment_id: int, db: Session = Depends(get_db)):
    d = db.get(ComponentDeployment, deployment_id)
    if not d:
        raise HTTPException(status_code=404, detail="Deployment mapping not found")
    db.delete(d)
    db.commit()
    return {"deleted": deployment_id}


@app.get("/api/supplylens/risk/score")
def risk_score(
    entity_type: str = "COMPONENT",
    entity_id: int = 1,
    db: Session = Depends(get_db),
):
    """Calculate deterministic explainable risk score for an entity."""
    factors: dict = {}
    if entity_type == "COMPONENT":
        comp = db.get(SoftwareComponent, entity_id)
        if not comp:
            raise HTTPException(status_code=404, detail="Component not found")
        criticals = [f for f in comp.findings if f.severity == "CRITICAL"]
        highs = [f for f in comp.findings if f.severity == "HIGH"]
        kevs = [f for f in comp.findings if f.cisa_kev]
        if comp.findings:
            factors["vulnerability_severity"] = 1.0 if criticals else (0.75 if highs else 0.5)
        if kevs:
            factors["known_exploitation"] = 1.0
        elif comp.findings:
            factors["known_exploitation"] = 0.3
        factors["business_criticality"] = comp.project.criticality / 10.0 if comp.project else 0.5
        factors["dependency_exposure"] = 0.8 if comp.direct else 0.4
        if comp.supplier:
            factors["supplier_risk"] = comp.supplier.risk_score / 100.0
    elif entity_type == "SUPPLIER":
        supplier = db.get(Supplier, entity_id)
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        factors["business_criticality"] = supplier.criticality / 10.0
        factors["data_sensitivity"] = {"HIGH": 1.0, "MEDIUM": 0.6, "LOW": 0.3}.get(supplier.data_sensitivity, 0.5)
        factors["supplier_risk"] = 0.8 if supplier.assessment_status == "PENDING_REVIEW" else 0.3
    else:
        raise HTTPException(status_code=422, detail=f"Unsupported entity_type: {entity_type}")
    score, band, breakdown = calculate_risk(factors)
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "risk_score": score,
        "risk_level": band,
        "factor_breakdown": breakdown,
        "methodology": "v1.0-explainable",
    }


@app.get("/api/supplylens/intelligence/health")
async def intelligence_health():
    """Report health status of external threat intelligence sources."""
    svc = VulnerabilityEnrichmentService()
    status = await svc.check_source_health()
    return status


@app.post("/api/supplylens/copilot/query")
async def copilot_query(req: CopilotQueryRequest, db: Session = Depends(get_db)):
    """AI Risk Copilot — deterministic grounded analysis with optional LLM enhancement."""
    copilot = RiskCopilotService(db)
    response = await copilot.query(req.prompt, project_id=req.project_id)
    return response


@app.post("/api/supplylens/mitigations", status_code=201)
def create_mitigation(req: CreateMitigationRequest, db: Session = Depends(get_db)):
    action = MitigationAction(
        finding_id=req.finding_id, component_id=req.component_id,
        supplier_id=req.supplier_id, title=req.title,
        action_type=req.action_type, notes=req.notes,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return {"id": action.id, "title": action.title, "status": action.status}


@app.patch("/api/supplylens/mitigations/{mitigation_id}/status")
def update_mitigation_status(mitigation_id: int, req: MitigationStatusRequest, db: Session = Depends(get_db)):
    from datetime import datetime as _dt
    action = db.get(MitigationAction, mitigation_id)
    if not action:
        raise HTTPException(status_code=404, detail="Mitigation action not found")
    action.status = req.status
    if req.status == "COMPLETED":
        action.completed_at = _dt.utcnow()
    db.commit()
    return {"id": action.id, "status": action.status}


@app.get("/api/supplylens/reports/findings.csv")
def export_findings_csv(db: Session = Depends(get_db)):
    """Export all findings as CSV for reporting."""
    import csv, io
    from fastapi.responses import StreamingResponse
    findings = db.scalars(
        select(ComponentFinding).order_by(ComponentFinding.severity, ComponentFinding.created_at)
    ).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Vulnerability", "Component", "Severity", "CVSS", "CISA_KEV", "Status", "Summary", "Fixed_Version", "Source", "Risk_Score", "Created"])
    for f in findings:
        writer.writerow([
            f.id, f.vulnerability_id,
            f.component.name if f.component else "",
            f.severity, f.cvss_score or "", "YES" if f.cisa_kev else "NO",
            f.status, (f.summary or "")[:120],
            f.fixed_version or "", f.source, f.risk_score,
            f.created_at.strftime("%Y-%m-%d"),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=supplylens-findings.csv"}
    )
