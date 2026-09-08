# API

Operational endpoints include `/api/facilities`, `/api/inventory`, `/api/products`, `/api/orders`, `/api/shipments`, and `/api/vehicles`.

Digital Twin endpoints include `/api/digital-twin`, `/api/digital-twin/map`, and `/api/events`.

Cyber endpoints include `/api/cyber/overview`, `/api/cyber/assets`, `/api/cyber/vulnerabilities`, `/api/cyber/controls`, `/api/cyber/incidents`, and `/api/cyber/what-if`.

Simulations are created with `POST /api/simulations`, started with `POST /api/simulations/{id}/start`, and responded to with `POST /api/incidents/{id}/respond`.

