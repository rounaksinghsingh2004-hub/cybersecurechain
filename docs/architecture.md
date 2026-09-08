# Architecture

The FastAPI backend is a modular monolith. SQLAlchemy models own the operational state; `DigitalTwinService` projects that state for both Admin and Cyber APIs. `EventService` records state changes. `SimulationEngine` uses the same assets, relationships, and control state but keeps effects within a synthetic simulation record.

The React frontend is split into operational and cyber navigation over the same REST API. It contains no duplicate operational dataset.

