from datetime import datetime
from enum import Enum
from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Status(str, Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    IN_TRANSIT = "IN_TRANSIT"
    DELAYED = "DELAYED"
    DELIVERED = "DELIVERED"


class Facility(Base):
    __tablename__ = "facilities"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    type: Mapped[str] = mapped_column(String(48), index=True)
    city: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(32), default=Status.ACTIVE.value)
    capacity: Mapped[int] = mapped_column(Integer)
    cyber_risk: Mapped[int] = mapped_column(Integer, default=0)
    inventory: Mapped[list["Inventory"]] = relationship(back_populates="facility")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    category: Mapped[str] = mapped_column(String(80))
    supplier: Mapped[str] = mapped_column(String(120))
    factory: Mapped[str] = mapped_column(String(120))
    price: Mapped[float] = mapped_column(Float)


class Inventory(Base):
    __tablename__ = "inventory"
    id: Mapped[int] = mapped_column(primary_key=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    batch_code: Mapped[str] = mapped_column(String(40))
    available: Mapped[int] = mapped_column(Integer, default=0)
    reserved: Mapped[int] = mapped_column(Integer, default=0)
    damaged: Mapped[int] = mapped_column(Integer, default=0)
    quarantined: Mapped[int] = mapped_column(Integer, default=0)
    facility: Mapped[Facility] = relationship(back_populates="inventory")
    product: Mapped[Product] = relationship()


class Vehicle(Base):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    driver: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(32), default=Status.ACTIVE.value)
    current_latitude: Mapped[float] = mapped_column(Float)
    current_longitude: Mapped[float] = mapped_column(Float)
    reported_latitude: Mapped[float] = mapped_column(Float)
    reported_longitude: Mapped[float] = mapped_column(Float)
    destination: Mapped[str] = mapped_column(String(120))
    gps_integrity: Mapped[str] = mapped_column(String(32), default="VERIFIED")


class Customer(Base):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))


class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), index=True)
    role: Mapped[str] = mapped_column(String(80))
    username: Mapped[str] = mapped_column(String(80), unique=True)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    account_status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    last_login: Mapped[str] = mapped_column(String(64))
    facility: Mapped[Facility] = relationship()


class OperationalAsset(Base):
    __tablename__ = "operational_assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    asset_type: Mapped[str] = mapped_column(String(32), index=True)
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"), index=True)
    zone: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="ACTIVE")
    criticality: Mapped[int] = mapped_column(Integer)
    firmware: Mapped[str] = mapped_column(String(48))
    network: Mapped[str] = mapped_column(String(64))
    cyber_status: Mapped[str] = mapped_column(String(32), default="CLEAR")
    facility: Mapped[Facility] = relationship()


class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    origin_facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id"))
    destination: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(40), index=True)
    cyber_status: Mapped[str] = mapped_column(String(96), default="CLEAR")
    eta: Mapped[str] = mapped_column(String(64))
    package_code: Mapped[str] = mapped_column(String(40))
    customer: Mapped[Customer] = relationship()
    origin: Mapped[Facility] = relationship()


class Shipment(Base):
    __tablename__ = "shipments"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    origin: Mapped[str] = mapped_column(String(120))
    destination: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40))
    package_count: Mapped[int] = mapped_column(Integer)
    eta: Mapped[str] = mapped_column(String(64))
    integrity: Mapped[str] = mapped_column(String(32), default="VERIFIED")
    order: Mapped[Order] = relationship()
    vehicle: Mapped[Vehicle] = relationship()


class CyberAsset(Base):
    __tablename__ = "cyber_assets"
    id: Mapped[int] = mapped_column(primary_key=True)
    asset_code: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    asset_type: Mapped[str] = mapped_column(String(48))
    facility_id: Mapped[int | None] = mapped_column(ForeignKey("facilities.id"), nullable=True)
    criticality: Mapped[int] = mapped_column(Integer)
    exposure: Mapped[int] = mapped_column(Integer)
    likelihood: Mapped[int] = mapped_column(Integer)
    impact: Mapped[int] = mapped_column(Integer)
    vulnerabilities: Mapped[list] = mapped_column(JSON, default=list)
    controls: Mapped[list] = mapped_column(JSON, default=list)
    compromised: Mapped[bool] = mapped_column(Boolean, default=False)
    facility: Mapped[Facility | None] = relationship()


class SecurityControl(Base):
    __tablename__ = "security_controls"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(48), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text)


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    entity_type: Mapped[str] = mapped_column(String(64))
    entity_id: Mapped[str] = mapped_column(String(64))
    facility_code: Mapped[str | None] = mapped_column(String(48), nullable=True)
    source: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text)
    previous_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_state: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class Simulation(Base):
    __tablename__ = "simulations"
    id: Mapped[int] = mapped_column(primary_key=True)
    scenario: Mapped[str] = mapped_column(String(64))
    target_asset_id: Mapped[int] = mapped_column(ForeignKey("cyber_assets.id"))
    status: Mapped[str] = mapped_column(String(32), default="CREATED")
    snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incidents"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    simulation_id: Mapped[int | None] = mapped_column(ForeignKey("simulations.id"), nullable=True)
    severity: Mapped[str] = mapped_column(String(24))
    status: Mapped[str] = mapped_column(String(32), default="DETECTED")
    facility_code: Mapped[str] = mapped_column(String(48))
    summary: Mapped[str] = mapped_column(Text)
    actions: Mapped[list] = mapped_column(JSON, default=list)
