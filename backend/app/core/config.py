from os import getenv


class Settings:
    database_url = getenv("DATABASE_URL", "sqlite:///./cybersecurechain.db")
    cors_origins = getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()

