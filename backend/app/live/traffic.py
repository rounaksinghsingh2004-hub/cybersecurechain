"""
Live Traffic Generator — continuously synthesizes network packet flows
and scores them through the real trained CIC-IDS2017 Random Forest ML model.

Features:
- Backed by genuine PCAP packet signatures from CIC-IDS2017
- Real-time classification: BENIGN, DDoS, PortScan, FTP-Patator, SSH-Patator, Web Attack, Bot, etc.
- In-memory circular buffer of live inspected packets for SOC Packet Inspection HUD
- Attack injection registry for manual and autonomous red-team campaigns
"""
import os
import random
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LiveEvent:
    facility_code: str
    asset_code: str
    label: str           # ML classification: BENIGN, DDoS, FTP-Patator, etc.
    confidence: float    # 0.0 – 1.0
    is_attack: bool
    packet_features: dict
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    scenario: Optional[str] = None


class TrafficGenerator:
    """
    Generates realistic network packet flows and classifies them with the
    trained Real IDS model. Maintains an injection registry and a recent
    packet buffer for real-time inspection.
    """

    def __init__(self):
        self._model = None
        self._features = None
        self._prototypes = {}
        self._model_loaded = False
        # facility_code -> (scenario, expires_at_epoch)
        self._attack_injections: dict[str, tuple[str, float]] = {}
        # Recent packets buffer (max 30 items)
        self._recent_packets = deque(maxlen=30)

    # ------------------------------------------------------------------
    # Model & Prototypes loading
    # ------------------------------------------------------------------

    def _load_model(self):
        if self._model_loaded:
            return
        try:
            import joblib
            base = os.path.join(os.path.dirname(__file__), "..", "simulation")
            model_path = os.path.abspath(os.path.join(base, "real_ids_model.pkl"))
            features_path = os.path.abspath(os.path.join(base, "real_ids_features.pkl"))
            proto_path = os.path.abspath(os.path.join(base, "attack_prototypes.pkl"))

            if os.path.exists(model_path) and os.path.exists(features_path):
                self._model = joblib.load(model_path)
                self._model.n_jobs = 1
                self._features = joblib.load(features_path)

            if os.path.exists(proto_path):
                self._prototypes = joblib.load(proto_path)
        except Exception as e:
            print(f"[TrafficGenerator] Model load error: {e}")
        self._model_loaded = True

    # ------------------------------------------------------------------
    # Injection API — called by manual or autonomous Red Team
    # ------------------------------------------------------------------

    def inject_attack(self, facility_code: str, scenario: str, duration_seconds: float = 60.0):
        """Register an attack injection for a facility for a limited time."""
        expires = time.time() + duration_seconds
        self._attack_injections[facility_code] = (scenario, expires)
        print(f"[TrafficGenerator] Injected {scenario} attack on {facility_code} for {duration_seconds}s")

    def clear_attack(self, facility_code: str):
        self._attack_injections.pop(facility_code, None)

    def active_attacks(self) -> dict[str, str]:
        """Return {facility_code: scenario} for currently active attacks."""
        now = time.time()
        expired = [k for k, (_, exp) in self._attack_injections.items() if now > exp]
        for k in expired:
            del self._attack_injections[k]
        return {k: v[0] for k, (v, _) in [(k, v) for k, v in self._attack_injections.items()]}

    # ------------------------------------------------------------------
    # Feature synthesis using genuine CIC-IDS2017 distributions
    # ------------------------------------------------------------------

    def _benign_features(self) -> dict:
        """Synthesize realistic BENIGN HTTP/HTTPS background traffic."""
        port = random.choice([80, 443, 8080, 3306, 5432, 22])
        flow_dur = random.randint(15000, 3000000)
        fwd_pkts = random.randint(2, 25)
        bwd_pkts = random.randint(1, 20)
        fwd_len_mean = random.uniform(80, 600)
        return {
            "Destination Port": port,
            "Flow Duration": flow_dur,
            "Total Fwd Packets": fwd_pkts,
            "Total Backward Packets": bwd_pkts,
            "Total Length of Fwd Packets": int(fwd_pkts * fwd_len_mean),
            "Fwd Packet Length Max": random.randint(200, 1460),
            "Fwd Packet Length Mean": fwd_len_mean,
            "Average Packet Size": fwd_len_mean * random.uniform(0.9, 1.2),
            "Subflow Fwd Bytes": int(fwd_pkts * fwd_len_mean),
            "Flow Bytes/s": random.uniform(500, 45000),
            "Flow Packets/s": random.uniform(2, 60),
            "Init_Win_bytes_forward": random.choice([29200, 65535, 14600, 8192]),
        }

    def _attack_features(self, scenario: str) -> dict:
        """
        Synthesize malicious packet features matching CIC-IDS2017 attack classes.
        Uses verified prototypes extracted from genuine PCAPs with jitter.
        """
        scenario_map = {
            "ACCOUNT_COMPROMISE": random.choice(["FTP-Patator", "SSH-Patator"]),
            "OT_DISRUPTION": "DDoS",
            "IOT_SPOOFING": "Bot",
            "RANSOMWARE_IMPACT": "DDoS",
            "INVENTORY_MANIPULATION": "Web Attack - Brute Force",
            "SUPPLIER_COMPROMISE": "Web Attack - Brute Force",
            "GPS_SPOOFING": "DDoS",
            "QR_TAMPERING": "PortScan",
        }
        
        target_attack = scenario_map.get(scenario, scenario)
        
        # If prototype is available from real dataset, apply jitter
        if target_attack in self._prototypes:
            proto = self._prototypes[target_attack].copy()
            jitter = random.uniform(0.92, 1.08)
            for k in ["Flow Duration", "Total Fwd Packets", "Flow Packets/s", "Flow Bytes/s", "Subflow Fwd Bytes"]:
                if k in proto:
                    proto[k] = proto[k] * jitter
            return proto
            
        # Fallback to structured feature templates matching the model's top importances
        base = self._benign_features()
        if scenario in ("ACCOUNT_COMPROMISE", "SSH-Patator", "FTP-Patator"):
            port = 22 if "SSH" in target_attack else 21
            base.update({
                "Destination Port": port,
                "Total Fwd Packets": random.randint(8, 25),
                "Fwd Packet Length Mean": random.uniform(30, 90),
                "Average Packet Size": random.uniform(40, 100),
                "Flow Duration": random.randint(200000, 800000),
                "Flow Packets/s": random.uniform(150, 400),
                "Flow Bytes/s": random.uniform(8000, 25000),
            })
        elif scenario in ("OT_DISRUPTION", "IOT_SPOOFING", "DDoS", "DoS Hulk"):
            base.update({
                "Destination Port": 80,
                "Total Fwd Packets": random.randint(500, 2000),
                "Fwd Packet Length Mean": random.uniform(40, 75),
                "Average Packet Size": random.uniform(50, 85),
                "Flow Duration": random.randint(10000, 80000),
                "Flow Bytes/s": random.uniform(2000000, 8000000),
                "Flow Packets/s": random.uniform(8000, 25000),
            })
        elif scenario in ("QR_TAMPERING", "PortScan"):
            base.update({
                "Destination Port": random.randint(1024, 65535),
                "Total Fwd Packets": random.randint(1, 3),
                "Fwd Packet Length Mean": random.uniform(0, 10),
                "Average Packet Size": random.uniform(0, 15),
                "Flow Duration": random.randint(1000, 10000),
                "Flow Packets/s": random.uniform(800, 3000),
            })
        else: # Web Attack
            base.update({
                "Destination Port": random.choice([80, 443, 8080]),
                "Total Fwd Packets": random.randint(4, 15),
                "Fwd Packet Length Max": random.randint(900, 1500),
                "Fwd Packet Length Mean": random.uniform(350, 800),
                "Average Packet Size": random.uniform(400, 950),
                "Flow Packets/s": random.uniform(50, 250),
            })
        return base

    # ------------------------------------------------------------------
    # Main generation & scoring method
    # ------------------------------------------------------------------

    def generate(self, facility_code: str, asset_code: str) -> LiveEvent:
        """
        Generate a single traffic event for the given asset. If an attack is
        active for this facility, uses attack-pattern features; otherwise BENIGN.
        Scores through the CIC-IDS2017 Random Forest model.
        """
        self._load_model()

        now = time.time()
        active_injection = None
        if facility_code in self._attack_injections:
            scenario, expires = self._attack_injections[facility_code]
            if now > expires:
                del self._attack_injections[facility_code]
            else:
                active_injection = scenario

        # Build packet features
        if active_injection:
            features = self._attack_features(active_injection)
        else:
            features = self._benign_features()

        # Run ML inference
        label = "BENIGN"
        confidence = random.uniform(0.91, 0.99)

        if self._model is not None and self._features is not None:
            try:
                import pandas as pd
                import numpy as np
                X = pd.DataFrame(0.0, index=[0], columns=self._features)
                for col, val in features.items():
                    if col in X.columns:
                        try:
                            X[col] = float(val)
                        except:
                            X[col] = 0.0
                X = X.replace([np.inf, -np.inf], 0).fillna(0)
                label = str(self._model.predict(X)[0])
                if hasattr(self._model, "predict_proba"):
                    proba = self._model.predict_proba(X)[0]
                    confidence = float(max(proba))
            except Exception as e:
                print(f"[TrafficGenerator] Inference error: {e}")

        is_attack = label.upper() != "BENIGN"

        event = LiveEvent(
            facility_code=facility_code,
            asset_code=asset_code,
            label=label,
            confidence=round(confidence, 3),
            is_attack=is_attack,
            packet_features={
                "dst_port": int(features.get("Destination Port", 80)),
                "flow_duration_us": int(features.get("Flow Duration", 0)),
                "total_fwd_pkts": int(features.get("Total Fwd Packets", 0)),
                "fwd_len_mean": round(float(features.get("Fwd Packet Length Mean", 0.0)), 1),
                "flow_bytes_per_s": round(float(features.get("Flow Bytes/s", 0.0)), 1),
                "flow_pkts_per_s": round(float(features.get("Flow Packets/s", 0.0)), 1),
            },
            scenario=active_injection,
        )

        # Store in circular buffer for packet inspector HUD
        self._recent_packets.append({
            "timestamp": event.timestamp,
            "facility": facility_code,
            "asset": asset_code,
            "classification": label,
            "confidence": event.confidence,
            "is_threat": is_attack,
            "metrics": event.packet_features,
        })

        return event

    def get_recent_packets(self) -> list[dict]:
        """Return the most recently analyzed packets for the visual HUD."""
        return list(self._recent_packets)
