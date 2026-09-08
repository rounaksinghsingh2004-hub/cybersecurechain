# CyberSecureChain

CyberSecureChain is a safe, fictional digital twin for **NEXORA Commerce & Logistics**. It joins supply-chain operations with a cybersecurity operations center so Admin, Red Team, and Blue Team inspect one shared model.

## What is implemented

- Deterministic relational seed data: 14 facilities, 100 products, 500 orders, 40 vehicles, 250 employees, 50 robots, 60 machines, 200 IoT assets, 40 OT assets, inventory, shipments, cyber assets, controls, and unified events.
- FastAPI domain services for inventory reservation, validated order transitions, Digital Twin state, transparent risk scoring, and centralized event recording.
- Safe Red Team simulations run against an in-database simulation snapshot. They do not scan, exploit, or contact real systems.
- Blue Team response actions and controls that alter modeled propagation. What-If compares the same scenario under current and hardened controls.
- React/Vite control tower with Admin/Cyber modes, Leaflet map, tables, drawers, timelines, simulation results, controls, and incidents.

## Run locally

Terminal 1:

```powershell
cd backend
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Terminal 2:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The development API uses SQLite by default. Set `DATABASE_URL` to PostgreSQL for a persistent deployment, or use Docker Compose:

```powershell
docker compose up --build
```

## Demo workflow

1. Open **Admin > Overview**, select `FC-JPR-01`, then inspect inventory, orders, fleet, and the Digital Twin.
2. Open **Cyber > Security Overview** and inspect the seeded warehouse account and associated assets.
3. In **Simulation**, select `ACCOUNT_COMPROMISE` and `USR-WH-ANITA`, then launch the safe simulation.
4. In **Incidents**, contain the generated incident; in **Controls**, enable MFA and segmentation.
5. Open **What-If** to compare propagation and business impact against the hardened environment.

## Safety boundary

All attack scenarios are abstract, deterministic database-state simulations on synthetic assets. The application never sends malicious traffic, scans a target, executes malware, uses credentials, or accesses external infrastructure.

More detail: [architecture](docs/architecture.md), [digital twin](docs/digital-twin.md), [simulation engine](docs/simulation-engine.md), [API](docs/api.md), and [testing](docs/testing.md).
