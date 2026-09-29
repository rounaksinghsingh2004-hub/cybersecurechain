import unittest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Facility, CyberAsset, Order, Customer
from app.live.autonomous_engine import autonomous_engine
from app.live.traffic import TrafficGenerator

def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

class AutonomousEngineTests(unittest.TestCase):
    def test_status_and_defaults(self):
        status = autonomous_engine.get_status()
        self.assertIn("adversary_enabled", status)
        self.assertIn("mitigation_enabled", status)
        self.assertIn("metrics", status)

    def test_launch_and_mitigation_cycle(self):
        db = session()
        facility = Facility(code="FC-TEST", name="Test Center", type="WAREHOUSE", city="Jaipur", latitude=26.9, longitude=75.8, capacity=100, cyber_risk=20)
        customer = Customer(name="Test Customer", city="Jaipur")
        db.add_all([facility, customer])
        db.flush()
        
        target = CyberAsset(asset_code="PLC-TEST", name="Test PLC", asset_type="PLC", facility_id=facility.id, criticality=9, exposure=8, likelihood=8, impact=9, vulnerabilities=[], controls=[])
        order = Order(number="ORD-TEST-1", customer_id=customer.id, origin_facility_id=facility.id, destination="Delhi", status="PAYMENT_CONFIRMED", eta="Tomorrow", package_code="PKG-1")
        db.add_all([target, order])
        db.commit()

        traffic_gen = TrafficGenerator()
        broadcasts = []
        async def mock_broadcast(msg):
            broadcasts.append(msg)

        # 1. Launch campaign
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        camp = loop.run_until_complete(
            autonomous_engine.launch_campaign(db, traffic_gen, mock_broadcast, forced_scenario="OT_DISRUPTION", forced_facility="FC-TEST")
        )
        self.assertIsNotNone(camp)
        self.assertEqual(camp["facility_code"], "FC-TEST")
        self.assertIn("FC-TEST", traffic_gen.active_attacks())

        # 2. Simulate IDS Detection
        loop.run_until_complete(
            autonomous_engine.handle_detection({"label": "DDoS", "confidence": 0.99}, db, mock_broadcast)
        )
        self.assertEqual(autonomous_engine.current_campaign["stage"], "ML_IDS_DETECTED")

        # 3. Simulate Autonomous SOAR Defense
        loop.run_until_complete(
            autonomous_engine.execute_soar_defense(db, traffic_gen, mock_broadcast)
        )
        self.assertEqual(autonomous_engine.current_campaign["stage"], "MITIGATED")
        self.assertNotIn("FC-TEST", traffic_gen.active_attacks())
        self.assertGreaterEqual(autonomous_engine.total_mitigated, 1)

if __name__ == "__main__":
    unittest.main()
