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


# ---------------------------------------------------------------------------
# SupplyLens AI Models — Software & Supplier Risk Intelligence Layer
# ---------------------------------------------------------------------------

class Supplier(Base):
    __tablename__ = "suppliers"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    category: Mapped[str] = mapped_column(String(64), default="SOFTWARE")
    description: Mapped[str] = mapped_column(Text, default="")
    business_owner: Mapped[str] = mapped_column(String(120), default="")
    criticality: Mapped[int] = mapped_column(Integer, default=5)
    tier: Mapped[str] = mapped_column(String(20), default="TIER_1")
    assessment_status: Mapped[str] = mapped_column(String(32), default="PENDING_REVIEW")
    contact_email: Mapped[str] = mapped_column(String(120), default="")
    last_assessment_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    evidence_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_sensitivity: Mapped[str] = mapped_column(String(32), default="MEDIUM")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    components: Mapped[list["SoftwareComponent"]] = relationship(back_populates="supplier")


class SoftwareProject(Base):
    __tablename__ = "software_projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(48), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[str] = mapped_column(String(48), default="1.0.0")
    repository_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    business_owner: Mapped[str] = mapped_column(String(120), default="")
    facility_id: Mapped[int | None] = mapped_column(ForeignKey("facilities.id"), nullable=True)
    criticality: Mapped[int] = mapped_column(Integer, default=5)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    facility: Mapped[Facility | None] = relationship()
    components: Mapped[list["SoftwareComponent"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    import_jobs: Mapped[list["SbomImportJob"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class SbomImportJob(Base):
    __tablename__ = "sbom_import_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("software_projects.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    format: Mapped[str] = mapped_column(String(32))  # CYCLONEDX_JSON, SPDX_JSON, MANUAL
    status: Mapped[str] = mapped_column(String(32), default="PENDING")
    component_count: Mapped[int] = mapped_column(Integer, default=0)
    relationship_count: Mapped[int] = mapped_column(Integer, default=0)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[SoftwareProject] = relationship(back_populates="import_jobs")


class SoftwareComponent(Base):
    __tablename__ = "software_components"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("software_projects.id"), index=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    version: Mapped[str] = mapped_column(String(64))
    ecosystem: Mapped[str] = mapped_column(String(48), default="generic")  # npm, pypi, maven, etc.
    purl: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    license: Mapped[str | None] = mapped_column(String(120), nullable=True)
    direct: Mapped[bool] = mapped_column(Boolean, default=True)
    scope: Mapped[str] = mapped_column(String(32), default="runtime")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    risk_level: Mapped[str] = mapped_column(String(20), default="LOW")
    raw_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    project: Mapped[SoftwareProject] = relationship(back_populates="components")
    supplier: Mapped[Supplier | None] = relationship(back_populates="components")
    findings: Mapped[list["ComponentFinding"]] = relationship(back_populates="component", cascade="all, delete-orphan")
    deployments: Mapped[list["ComponentDeployment"]] = relationship(back_populates="component", cascade="all, delete-orphan")


class ComponentDependency(Base):
    __tablename__ = "component_dependencies"
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("software_projects.id"), index=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("software_components.id"), index=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("software_components.id"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(48), default="DEPENDS_ON")


class ComponentFinding(Base):
    __tablename__ = "component_findings"
    id: Mapped[int] = mapped_column(primary_key=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("software_components.id"), index=True)
    vulnerability_id: Mapped[str] = mapped_column(String(64), index=True)
    source: Mapped[str] = mapped_column(String(48), default="OSV")
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    cvss_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    cisa_kev: Mapped[bool] = mapped_column(Boolean, default=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[str] = mapped_column(Text, default="")
    affected_versions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fixed_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="OPEN")  # OPEN, IN_TRIAGE, MITIGATED, ACCEPTED
    confidence: Mapped[str] = mapped_column(String(32), default="HIGH")
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    component: Mapped[SoftwareComponent] = relationship(back_populates="findings")
    mitigations: Mapped[list["MitigationAction"]] = relationship(back_populates="finding", cascade="all, delete-orphan")


class ComponentDeployment(Base):
    __tablename__ = "component_deployments"
    id: Mapped[int] = mapped_column(primary_key=True)
    component_id: Mapped[int] = mapped_column(ForeignKey("software_components.id"), index=True)
    service_name: Mapped[str] = mapped_column(String(120))
    cyber_asset_id: Mapped[int | None] = mapped_column(ForeignKey("cyber_assets.id"), nullable=True)
    operational_asset_id: Mapped[int | None] = mapped_column(ForeignKey("operational_assets.id"), nullable=True)
    facility_id: Mapped[int | None] = mapped_column(ForeignKey("facilities.id"), nullable=True)
    business_process: Mapped[str] = mapped_column(String(160), default="Fulfillment Operations")
    mapping_type: Mapped[str] = mapped_column(String(32), default="VERIFIED")  # VERIFIED, USER_MAPPED, INFERRED, SYNTHETIC
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    component: Mapped[SoftwareComponent] = relationship(back_populates="deployments")
    cyber_asset: Mapped[CyberAsset | None] = relationship()
    operational_asset: Mapped[OperationalAsset | None] = relationship()
    facility: Mapped[Facility | None] = relationship()


class RiskSnapshot(Base):
    __tablename__ = "risk_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(32))  # PROJECT, COMPONENT, SUPPLIER, FINDING
    entity_id: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(20))
    factor_breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    available_factors: Mapped[list] = mapped_column(JSON, default=list)
    missing_factors: Mapped[list] = mapped_column(JSON, default=list)
    methodology_version: Mapped[str] = mapped_column(String(32), default="v1.0-explainable")
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MitigationAction(Base):
    __tablename__ = "mitigation_actions"
    id: Mapped[int] = mapped_column(primary_key=True)
    finding_id: Mapped[int | None] = mapped_column(ForeignKey("component_findings.id"), nullable=True)
    component_id: Mapped[int | None] = mapped_column(ForeignKey("software_components.id"), nullable=True)
    supplier_id: Mapped[int | None] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160))
    action_type: Mapped[str] = mapped_column(String(48))
    status: Mapped[str] = mapped_column(String(32), default="PROPOSED")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    finding: Mapped[ComponentFinding | None] = relationship(back_populates="mitigations")

