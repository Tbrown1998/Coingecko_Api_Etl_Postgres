import os
from dotenv import load_dotenv

load_dotenv()

# Postgres master connection (postgres default db) used for DB creation
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "Wmdwmdwmd1")
POSTGRES_DB = os.getenv("POSTGRES_DB", "crypto_db")  # target DB name

# SQLAlchemy connection string template (will be formatted by code)
# note: password may contain special chars; SQLAlchemy handles them in a URI if encoded.
SQLALCHEMY_DRIVER = "postgresql+psycopg2"

# Email
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_RECEIVERS = [e.strip() for e in os.getenv("EMAIL_RECEIVERS", "").split(",") if e.strip()]

# App
SCHEDULE_TIME = os.getenv("SCHEDULE_TIME", "09:00")
COINGECKO_PER_PAGE = int(os.getenv("COINGECKO_PER_PAGE", 250))
COINGECKO_PAGE = int(os.getenv("COINGECKO_PAGE", 1))
