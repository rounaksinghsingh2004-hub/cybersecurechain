from os import getenv


_DEFAULT_CORS = ",".join([
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    # Vercel production alias
    "https://frontend-mauve-chi-80.vercel.app",
    # Vercel preview deployments (any rounak project)
    "https://frontend-3anpcxftr-rounak-singhs-projects-396c5b0e.vercel.app",
    "https://frontend-na1h648km-rounak-singhs-projects-396c5b0e.vercel.app",
])


class Settings:
    database_url = getenv("DATABASE_URL", "sqlite:///./cybersecurechain.db")
    cors_origins = getenv("CORS_ORIGINS", _DEFAULT_CORS).split(",")


settings = Settings()

