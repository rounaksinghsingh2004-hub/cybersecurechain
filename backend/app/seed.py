from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Customer, CyberAsset, Employee, Event, Facility, Inventory, OperationalAsset, Order, Product, SecurityControl, Shipment, Vehicle
from app.services.events import EventService


FACILITIES = [
    ("SUP-DEL-01", "Delhi Supplier Gateway", "SUPPLIER", "Delhi", 28.6139, 77.2090, 18000),
    ("SUP-AHM-01", "Ahmedabad Supplier Park", "SUPPLIER", "Ahmedabad", 23.0225, 72.5714, 16000),
    ("MFG-JPR-01", "Jaipur Assembly Plant", "FACTORY", "Jaipur", 26.9124, 75.7873, 35000),
    ("MFG-PUN-01", "Pune Electronics Plant", "FACTORY", "Pune", 18.5204, 73.8567, 32000),
    ("FC-JPR-01", "Jaipur Fulfillment Center", "WAREHOUSE", "Jaipur", 26.8467, 75.8098, 65000),
    ("FC-MUM-01", "Mumbai Fulfillment Center", "WAREHOUSE", "Mumbai", 19.0760, 72.8777, 72000),
    ("FC-BLR-01", "Bengaluru Fulfillment Center", "WAREHOUSE", "Bengaluru", 12.9716, 77.5946, 58000),
    ("FC-HYD-01", "Hyderabad Fulfillment Center", "WAREHOUSE", "Hyderabad", 17.3850, 78.4867, 54000),
    ("DC-DEL-01", "Delhi Distribution Center", "DISTRIBUTION_CENTER", "Delhi", 28.7041, 77.1025, 45000),
    ("DC-KOL-01", "Kolkata Distribution Center", "DISTRIBUTION_CENTER", "Kolkata", 22.5726, 88.3639, 40000),
    ("HUB-JPR-01", "Jaipur Delivery Hub", "DELIVERY_HUB", "Jaipur", 26.8850, 75.7610, 12000),
    ("HUB-DEL-01", "Delhi Delivery Hub", "DELIVERY_HUB", "Delhi", 28.6300, 77.2400, 14000),
    ("HUB-MUM-01", "Mumbai Delivery Hub", "DELIVERY_HUB", "Mumbai", 19.1000, 72.9000, 14000),
    ("HUB-BLR-01", "Bengaluru Delivery Hub", "DELIVERY_HUB", "Bengaluru", 12.9400, 77.6200, 13000),
]


def seed(db: Session) -> None:
    if db.scalar(select(Facility.id).limit(1)):
        return
    facilities = []
    for code, name, type_, city, lat, lng, capacity in FACILITIES:
        facility = Facility(code=code, name=name, type=type_, city=city, latitude=lat, longitude=lng,
                            capacity=capacity, cyber_risk=68 if code == "FC-JPR-01" else 20 + (len(code) * 3) % 35)
        db.add(facility); facilities.append(facility)
    db.flush()
    warehouses = [f for f in facilities if f.type == "WAREHOUSE"]
    products = []
    categories = ["Consumer Electronics", "Home Essentials", "Mobility", "Health & Care", "Industrial Supplies"]
    for i in range(1, 101):
        product = Product(sku=f"NX-{i:04d}", name=f"Nexora {categories[(i - 1) % len(categories)]} Item {i:03d}",
                          category=categories[(i - 1) % len(categories)], supplier="Delhi Supplier Gateway" if i % 2 else "Ahmedabad Supplier Park",
                          factory="Jaipur Assembly Plant" if i % 3 else "Pune Electronics Plant", price=499 + (i * 73) % 4200)
        db.add(product); products.append(product)
    db.flush()
    for warehouse in warehouses:
        for product in products:
            amount = 80 + ((warehouse.id * product.id * 19) % 550)
            db.add(Inventory(facility_id=warehouse.id, product_id=product.id, batch_code=f"B{warehouse.id:02d}{product.id:04d}",
                             available=amount, reserved=(product.id * 3) % 38, damaged=product.id % 4, quarantined=1 if product.id % 31 == 0 else 0))
    customers = []
    for i in range(1, 101):
        c = Customer(name=f"Customer {i:03d}", city=["Delhi", "Jaipur", "Mumbai", "Bengaluru", "Hyderabad", "Kolkata"][i % 6]); db.add(c); customers.append(c)
    db.flush()
    for i in range(1, 251):
        facility = warehouses[i % len(warehouses)]
        db.add(Employee(employee_code=f"EMP-{i:04d}", name=f"Nexora Employee {i:03d}", facility_id=facility.id,
                        role=["Warehouse Associate", "Operations Lead", "Security Analyst", "Fleet Coordinator"][i % 4], username=f"employee{i:03d}",
                        mfa_enabled=i % 5 != 0, account_status="ACTIVE", last_login="2026-09-08 09:30"))
    asset_counts = {"ROBOT": 50, "MACHINE": 60, "IOT": 200, "OT": 40}
    for asset_type, count in asset_counts.items():
        for i in range(1, count + 1):
            facility = warehouses[i % len(warehouses)]
            db.add(OperationalAsset(asset_code=f"{asset_type}-{i:03d}", name=f"{asset_type.title()} {i:03d}", asset_type=asset_type,
                                    facility_id=facility.id, zone=["Receiving", "Storage", "Picking", "Packing", "Loading"][i % 5],
                                    status="ACTIVE", criticality=4 + i % 6, firmware=f"v{1 + i % 3}.{i % 10}", network="Warehouse OT" if asset_type in {"OT", "MACHINE", "ROBOT"} else "Warehouse IoT", cyber_status="CLEAR"))
    vehicles = []
    city_coords = {f.city: (f.latitude, f.longitude) for f in facilities}
    for i in range(1, 41):
        city = ["Jaipur", "Delhi", "Mumbai", "Bengaluru", "Hyderabad"][i % 5]
        lat, lng = city_coords[city]
        vehicle = Vehicle(code=f"NX-TRK-{i:03d}", driver=f"Driver {i:02d}", status="IN_TRANSIT" if i % 3 else "AVAILABLE",
                          current_latitude=lat + (i % 4) * .013, current_longitude=lng + (i % 5) * .011,
                          reported_latitude=lat + (i % 4) * .013, reported_longitude=lng + (i % 5) * .011,
                          destination="Delhi Distribution Center" if city == "Jaipur" else "Nearest Delivery Hub", gps_integrity="VERIFIED")
        db.add(vehicle); vehicles.append(vehicle)
    db.flush()
    for i in range(1, 501):
        warehouse = warehouses[i % len(warehouses)]
        order = Order(number=f"ORD-{10481 + i}", customer_id=customers[i % len(customers)].id, origin_facility_id=warehouse.id,
                      destination=f"{customers[i % len(customers)].city} customer zone", status=["CREATED", "INVENTORY_RESERVED", "PICKED", "PACKED", "IN_TRANSIT", "OUT_FOR_DELIVERY"][i % 6],
                      eta=(datetime.utcnow() + timedelta(hours=4 + i % 48)).strftime("%d %b, %H:%M"), package_code=f"PKG-{829103 + i}")
        db.add(order); db.flush()
        if i % 2 == 0:
            db.add(Shipment(code=f"SHP-{70000 + i}", order_id=order.id, vehicle_id=vehicles[i % len(vehicles)].id,
                            origin=warehouse.name, destination=order.destination, status="IN_TRANSIT", package_count=1,
                            eta=order.eta, integrity="VERIFIED"))
    asset_specs = [
        ("USR-WH-ANITA", "Anita Sharma Warehouse Account", "ACCOUNT", "FC-JPR-01", 8, 8, 8, 8, ["MISSING_MFA", "EXCESSIVE_PRIVILEGE"], ["MFA", "LEAST_PRIVILEGE"]),
        ("SRV-INV-JPR", "Jaipur Inventory Server", "SERVER", "FC-JPR-01", 9, 7, 7, 9, ["OUTDATED_SOFTWARE", "INSUFFICIENT_MONITORING"], ["MONITORING", "BACKUP"]),
        ("DB-ORD-JPR", "Order Database", "DATABASE", "FC-JPR-01", 10, 6, 6, 10, ["EXCESSIVE_PRIVILEGE"], ["LEAST_PRIVILEGE", "BACKUP"]),
        ("OT-GW-JPR", "Warehouse OT Gateway", "OT", "FC-JPR-01", 9, 5, 7, 9, ["POOR_SEGMENTATION"], ["NETWORK_SEGMENTATION"]),
        ("PLC-SORT-JPR", "Sorting PLC", "PLC", "FC-JPR-01", 9, 3, 5, 9, ["WEAK_DEVICE_IDENTITY"], ["DEVICE_IDENTITY", "NETWORK_SEGMENTATION"]),
        ("RBT-SORT-01", "Sorting Robot 01", "ROBOT", "FC-JPR-01", 7, 3, 4, 7, ["WEAK_DEVICE_IDENTITY"], ["DEVICE_IDENTITY"]),
        ("IOT-RFID-JPR", "RFID Reader East Dock", "IOT", "FC-JPR-01", 6, 6, 6, 6, ["EXTERNAL_EXPOSURE"], ["DEVICE_IDENTITY", "MONITORING"]),
        ("SUP-API-DEL", "Supplier API Connection", "CONNECTION", "SUP-DEL-01", 7, 9, 7, 8, ["UNTRUSTED_CONNECTION", "WEAK_AUTHENTICATION"], ["SUPPLIER_AUTHENTICATION"]),
        ("GPS-TRK-001", "Truck GPS Gateway", "GPS", "FC-JPR-01", 6, 7, 6, 6, ["WEAK_DEVICE_IDENTITY"], ["DEVICE_IDENTITY", "MONITORING"]),
    ]
    facilities_by_code = {f.code: f for f in facilities}
    for code, name, type_, facility_code, crit, exposure, likelihood, impact, vulns, controls in asset_specs:
        db.add(CyberAsset(asset_code=code, name=name, asset_type=type_, facility_id=facilities_by_code[facility_code].id,
                          criticality=crit, exposure=exposure, likelihood=likelihood, impact=impact, vulnerabilities=vulns, controls=controls))
    for code, name, description, enabled in [
        ("MFA", "Multi-factor authentication", "Blocks account-compromise propagation at the identity boundary.", False),
        ("LEAST_PRIVILEGE", "Least privilege", "Stops lateral access to unrelated inventory and order systems.", False),
        ("NETWORK_SEGMENTATION", "Network segmentation", "Stops modeled IT-to-OT propagation.", False),
        ("SUPPLIER_AUTHENTICATION", "Supplier authentication", "Limits supplier-originated propagation.", False),
        ("MONITORING", "Security monitoring", "Improves event correlation and detection.", True),
        ("BACKUP", "Recoverable backup", "Enables modeled restoration after containment.", True),
    ]:
        db.add(SecurityControl(code=code, name=name, description=description, enabled=enabled))
    db.flush()
    EventService.record(db, "ORDER_CREATED", "OPERATIONS", "order", "ORD-10482", "Demo order ORD-10482 created for Jaipur customer zone", "FC-JPR-01", "SEED")
    EventService.record(db, "INVENTORY_RESERVED", "INVENTORY", "order", "ORD-10482", "Inventory reserved from FC-JPR-01", "FC-JPR-01", "SEED")
    EventService.record(db, "SHIPMENT_DISPATCHED", "LOGISTICS", "order", "ORD-10482", "Demo package assigned to NX-TRK-002", "FC-JPR-01", "SEED")
    db.commit()
