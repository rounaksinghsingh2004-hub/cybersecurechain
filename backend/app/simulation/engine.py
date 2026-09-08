from sqlalchemy import select
from sqlalchemy.orm import Session

from app.digital_twin.service import asset_payload
from app.models import CyberAsset, Incident, Order, SecurityControl, Simulation
from app.services.events import EventService


SCENARIOS = {
    "ACCOUNT_COMPROMISE", "INVENTORY_MANIPULATION", "GPS_SPOOFING", "QR_TAMPERING",
    "SUPPLIER_COMPROMISE", "IOT_SPOOFING", "OT_DISRUPTION", "RANSOMWARE_IMPACT",
}

SCENARIO_GUIDANCE = {
    "ACCOUNT_COMPROMISE": ("MISSING_MFA", "The modeled account is missing a second authentication factor and has broader access than its warehouse role requires.", ["MFA", "LEAST_PRIVILEGE", "MONITORING"]),
    "INVENTORY_MANIPULATION": ("EXCESSIVE_PRIVILEGE", "Inventory write access is broader than the modeled operational role requires.", ["LEAST_PRIVILEGE", "MONITORING", "BACKUP"]),
    "GPS_SPOOFING": ("WEAK_DEVICE_IDENTITY", "The modeled GPS feed lacks a strong device identity and monitoring boundary.", ["DEVICE_IDENTITY", "MONITORING"]),
    "QR_TAMPERING": ("WEAK_DEVICE_IDENTITY", "The modeled scanning path lacks a strong trusted-device validation step.", ["DEVICE_IDENTITY", "MONITORING"]),
    "SUPPLIER_COMPROMISE": ("UNTRUSTED_CONNECTION", "The modeled supplier connection has insufficient authentication and trust validation.", ["SUPPLIER_AUTHENTICATION", "MONITORING"]),
    "IOT_SPOOFING": ("WEAK_DEVICE_IDENTITY", "The modeled IoT endpoint lacks strong device identity and observation controls.", ["DEVICE_IDENTITY", "MONITORING", "NETWORK_SEGMENTATION"]),
    "OT_DISRUPTION": ("POOR_SEGMENTATION", "The modeled IT-to-OT boundary does not have an active network segmentation control.", ["NETWORK_SEGMENTATION", "MONITORING", "BACKUP"]),
    "RANSOMWARE_IMPACT": ("OUTDATED_SOFTWARE", "The modeled service has an outdated-software condition and incomplete recovery hardening.", ["MONITORING", "BACKUP", "NETWORK_SEGMENTATION"]),
}


class SimulationEngine:
    def __init__(self, db: Session):
        self.db = db

    def launch(self, scenario: str, target_asset_id: int) -> Simulation:
        if scenario not in SCENARIOS:
            raise ValueError("Unsupported safe simulation scenario")
        target = self.db.get(CyberAsset, target_asset_id)
        if not target:
            raise ValueError("Target asset not found")
        snapshot = {"target": asset_payload(target), "controls": self._controls(), "assets": [asset_payload(asset) for asset in self.db.scalars(select(CyberAsset)).all()]}
        simulation = Simulation(scenario=scenario, target_asset_id=target.id, status="CREATED", snapshot=snapshot)
        self.db.add(simulation)
        self.db.flush()
        EventService.record(self.db, "SIMULATION_CREATED", "SIMULATION", "simulation", simulation.id, f"Safe {scenario} simulation prepared against {target.name}", target.facility.code if target.facility else None, "RED_TEAM")
        return simulation

    def automatic_attack(self) -> Simulation:
        target = self.db.scalar(select(CyberAsset).where(CyberAsset.asset_code == "USR-WH-ANITA"))
        if not target:
            raise ValueError("The seeded automatic-demo target is unavailable")
        return self.start(self.launch("ACCOUNT_COMPROMISE", target.id).id)

    def start(self, simulation_id: int) -> Simulation:
        simulation = self.db.get(Simulation, simulation_id)
        if not simulation or simulation.status not in {"CREATED", "STOPPED"}:
            raise ValueError("Simulation cannot be started")
        target = self.db.get(CyberAsset, simulation.target_asset_id)
        if not target:
            raise ValueError("Simulation target not found")

        # Evaluate launch-time state only. Never mutate operational orders or primary cyber assets.
        result = self._evaluate(simulation.scenario, target, simulation.snapshot.get("controls", {}))
        simulation.status = "COMPLETED"
        simulation.result = result
        EventService.record(self.db, "SIMULATION_COMPLETED", "SIMULATION", "simulation", simulation.id, f"Safe simulation evaluated {result['affected_assets']} synthetic assets without changing the primary twin", target.facility.code if target.facility else None, "RED_TEAM")
        if result["affected_assets"] > 1:
            incident = Incident(code=f"INC-SIM-{simulation.id:04d}", simulation_id=simulation.id, severity="HIGH" if result["affected_assets"] < 4 else "CRITICAL", facility_code=target.facility.code if target.facility else "EXTERNAL", summary=f"{simulation.scenario} affecting {result['affected_assets']} synthetic digital-twin assets")
            self.db.add(incident)
            EventService.record(self.db, "INCIDENT_CREATED", "CYBER", "incident", incident.code, incident.summary, incident.facility_code, "DETECTION_ENGINE")
        return simulation

    def respond(self, incident_id: int, action: str) -> Incident:
        incident = self.db.get(Incident, incident_id)
        if not incident:
            raise ValueError("Incident not found")
        control_map = {"ENABLE_MFA": "MFA", "APPLY_SEGMENTATION": "NETWORK_SEGMENTATION", "REDUCE_PRIVILEGE": "LEAST_PRIVILEGE", "INCREASE_MONITORING": "MONITORING", "RESTORE_BACKUP": "BACKUP"}
        if action in control_map:
            control = self.db.scalar(select(SecurityControl).where(SecurityControl.code == control_map[action]))
            if control:
                control.enabled = True
        incident.actions = [*incident.actions, action]
        if action in {"ISOLATE_ASSET", "DISABLE_ACCOUNT", "BLOCK_CONNECTION"}:
            incident.status = "CONTAINED"
        if action == "RESTORE_BACKUP":
            incident.status = "RECOVERED"
        EventService.record(self.db, "BLUE_TEAM_ACTION", "RECOVERY", "incident", incident.code, f"Blue Team applied {action}", incident.facility_code, "BLUE_TEAM")
        return incident

    def compare(self, scenario: str, target_asset_id: int) -> dict:
        target = self.db.get(CyberAsset, target_asset_id)
        if not target or scenario not in SCENARIOS:
            raise ValueError("Invalid scenario or target")
        current = self._project(scenario, target, self._controls())
        hardened_controls = {**self._controls(), "MFA": True, "LEAST_PRIVILEGE": True, "NETWORK_SEGMENTATION": True, "SUPPLIER_AUTHENTICATION": True, "MONITORING": True, "BACKUP": True}
        return {"scenario": scenario, "target": target.asset_code, "current": current, "hardened": self._project(scenario, target, hardened_controls)}

    def _evaluate(self, scenario: str, target: CyberAsset, controls: dict[str, bool]) -> dict:
        reached, blocked_by = self._reachable_assets(scenario, target, controls)
        control_gap, root_cause, recommended_controls = SCENARIO_GUIDANCE[scenario]
        affected_orders = self._affected_order_count(target, len(reached))
        timeline = [{"step": index + 1, "asset": asset.asset_code, "name": asset.name, "event": "SIMULATED_INITIAL_ACCESS" if index == 0 else "SIMULATED_PROPAGATION", "state": "AFFECTED"} for index, asset in enumerate(reached)]
        if blocked_by:
            timeline.append({"step": len(timeline) + 1, "asset": blocked_by, "name": blocked_by.replace("_", " ").title(), "event": "SIMULATED_CONTROL_BOUNDARY", "state": "BLOCKED"})
        downtime = len(reached) * 18
        missing_controls = [control for control in recommended_controls if not controls.get(control, False)]
        return {"initial_target": target.asset_code, "affected_assets": len(reached), "affected_orders": affected_orders, "affected_packages": affected_orders, "affected_shipments": affected_orders // 2, "affected_customers": affected_orders, "downtime_minutes": downtime, "sla_impact": f"{affected_orders} orders at risk" if affected_orders else "No modeled order disruption", "estimated_revenue_loss": affected_orders * 2800, "recovery_cost": len(reached) * 15000, "total_estimated_impact": affected_orders * 2800 + len(reached) * 15000, "blocked_by": blocked_by, "path": [asset.asset_code for asset in reached], "timeline": timeline, "root_cause": root_cause, "primary_control_gap": control_gap, "accountability": {"affected_component": target.name, "finding": "This is a modeled control-design gap, not individual blame."}, "improvements": [f"Enable {control.replace('_', ' ').title()}" for control in missing_controls] or ["Keep the active controls monitored and tested."], "simulated": True}

    def _project(self, scenario: str, target: CyberAsset, controls: dict[str, bool]) -> dict:
        reached, blocked_by = self._reachable_assets(scenario, target, controls)
        orders = self._affected_order_count(target, len(reached))
        return {"affected_assets": len(reached), "affected_orders": orders, "affected_packages": orders, "affected_shipments": orders // 2, "downtime_minutes": len(reached) * 18, "estimated_revenue_loss": orders * 2800, "blocked_by": blocked_by}

    def _reachable_assets(self, scenario: str, target: CyberAsset, controls: dict[str, bool]) -> tuple[list[CyberAsset], str | None]:
        reached = [target]
        if scenario == "ACCOUNT_COMPROMISE" and controls.get("MFA", False):
            return reached, "MFA"
        if scenario == "SUPPLIER_COMPROMISE" and controls.get("SUPPLIER_AUTHENTICATION", False):
            return reached, "SUPPLIER_AUTHENTICATION"
        blocked_by = None
        for asset in self.db.scalars(select(CyberAsset).where(CyberAsset.facility_id == target.facility_id)).all():
            if asset.id == target.id:
                continue
            if controls.get("NETWORK_SEGMENTATION", False) and asset.asset_type in {"OT", "PLC", "ROBOT"}:
                blocked_by = blocked_by or "NETWORK_SEGMENTATION"
                continue
            if controls.get("LEAST_PRIVILEGE", False) and asset.asset_type in {"DATABASE", "ORDER_SYSTEM"}:
                blocked_by = blocked_by or "LEAST_PRIVILEGE"
                continue
            reached.append(asset)
        return reached, blocked_by

    def _affected_order_count(self, target: CyberAsset, asset_count: int) -> int:
        return self.db.query(Order).filter(Order.origin_facility_id == target.facility_id).count() if asset_count > 1 and target.facility_id is not None else 0

    def _controls(self) -> dict[str, bool]:
        return {control.code: control.enabled for control in self.db.scalars(select(SecurityControl)).all()}
