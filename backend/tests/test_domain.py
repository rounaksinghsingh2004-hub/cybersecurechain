import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.digital_twin.service import risk_score
from app.models import Base, CyberAsset, Facility, Inventory, Order, Product, Customer
from app.services.operations import OperationsService
from app.simulation.engine import SimulationEngine


def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


class DomainTests(unittest.TestCase):
    def test_risk_score_is_transparent_and_normalized(self):
        asset = CyberAsset(asset_code="TEST", name="Test", asset_type="SERVER", criticality=10, exposure=10, likelihood=10, impact=10, vulnerabilities=[], controls=[])
        self.assertEqual(risk_score(asset), 100)

    def test_inventory_reservation_is_atomic_and_never_negative(self):
        db = session(); facility = Facility(code="FC-T", name="Test FC", type="WAREHOUSE", city="Jaipur", latitude=1, longitude=1, capacity=10, cyber_risk=1)
        product = Product(sku="SKU-T", name="Test Product", category="Test", supplier="S", factory="F", price=1); customer = Customer(name="C", city="Jaipur")
        db.add_all([facility, product, customer]); db.flush()
        inventory = Inventory(facility_id=facility.id, product_id=product.id, batch_code="B1", available=5, reserved=0); db.add(inventory)
        order = Order(number="ORD-T", customer_id=customer.id, origin_facility_id=facility.id, destination="Test", status="PAYMENT_CONFIRMED", eta="Tomorrow", package_code="PKG-T"); db.add(order); db.commit()
        OperationsService.reserve_inventory(db, inventory.id, 4, order)
        self.assertEqual((inventory.available, inventory.reserved), (1, 4))
        with self.assertRaises(ValueError):
            OperationsService.reserve_inventory(db, inventory.id, 2, order)
        self.assertEqual(inventory.available, 1)

    def test_invalid_order_transition_is_rejected(self):
        db = session(); facility = Facility(code="FC-S", name="State FC", type="WAREHOUSE", city="Jaipur", latitude=1, longitude=1, capacity=10, cyber_risk=1); customer = Customer(name="C", city="Jaipur")
        db.add_all([facility, customer]); db.flush(); order = Order(number="ORD-S", customer_id=customer.id, origin_facility_id=facility.id, destination="Test", status="CREATED", eta="Tomorrow", package_code="PKG-S"); db.add(order); db.commit()
        with self.assertRaises(ValueError):
            OperationsService.transition_order(db, order.id, "DELIVERED")
        self.assertEqual(order.status, "CREATED")

    def test_simulation_does_not_mutate_primary_operational_state(self):
        db = session()
        facility = Facility(code="FC-SIM", name="Simulation FC", type="WAREHOUSE", city="Jaipur", latitude=1, longitude=1, capacity=10, cyber_risk=1)
        customer = Customer(name="C", city="Jaipur")
        db.add_all([facility, customer]); db.flush()
        target = CyberAsset(asset_code="USR-SIM", name="Simulation Account", asset_type="ACCOUNT", facility_id=facility.id, criticality=8, exposure=8, likelihood=8, impact=8, vulnerabilities=["MISSING_MFA"], controls=["MFA"])
        peer = CyberAsset(asset_code="SRV-SIM", name="Simulation Server", asset_type="SERVER", facility_id=facility.id, criticality=9, exposure=7, likelihood=7, impact=9, vulnerabilities=[], controls=[])
        order = Order(number="ORD-SIM", customer_id=customer.id, origin_facility_id=facility.id, destination="Test", status="IN_TRANSIT", eta="Tomorrow", package_code="PKG-SIM")
        db.add_all([target, peer, order]); db.commit()
        simulation = SimulationEngine(db).launch("ACCOUNT_COMPROMISE", target.id)
        SimulationEngine(db).start(simulation.id)
        self.assertFalse(target.compromised)
        self.assertFalse(peer.compromised)
        self.assertEqual(order.status, "IN_TRANSIT")
