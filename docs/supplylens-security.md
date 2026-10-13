# SupplyLens AI: Security, Safety Boundaries & Data Governance

## 1. Non-Negotiable Safety Boundaries

As an academic university Project-Based Learning (PBL) prototype, CyberSecureChain with SupplyLens AI enforces strict ethical and operational boundaries:

1. **Zero External Attack Traffic:** Under no circumstances does the simulation engine send probe packets, exploit payloads, or malicious traffic to external networks, vendor servers, or public IPs.
2. **Safe In-Memory Snapshot Isolation:** Attack simulations execute against isolated memory clones of digital twin state. The primary operational database (orders, shipments, inventory records) is never mutated during adversary modeling.
3. **Synthetic Demo Data Grounding:** Synthetic demo records are explicitly labeled with `data_label: "SYNTHETIC_DEMO"` to prevent conflation with real-world intelligence.
4. **Input Sanitization & Schema Bounds:** SBOM uploads are capped at 10MB (`MAX_SBOM_BYTES`). All JSON payloads are validated against strict schema types before database ingestion to prevent arbitrary code execution or denial-of-service.
5. **No Blind External Trust:** When querying third-party threat feeds (OSV.dev), responses are validated, sanitized, and stored with confidence tags (`LIVE_OSV`, `CACHED_OSV`, `CISA_KEV`). Network failure automatically falls back to curated local intelligence.

---

## 2. Secrets & Credential Protection

- **No Secrets in Source:** No API keys, database passwords, or private tokens are hardcoded in git repository history or committed files.
- **Environment Isolation:** Local credentials (`.env.local`, `.env.*`) are strictly ignored via `.gitignore`.
- **Public Model Usability:** The core application, deterministic risk scoring, and AI Risk Copilot function completely without requiring any paid external API keys.
