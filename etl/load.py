from sqlalchemy import create_engine, text
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from configs import settings
from etl.utils import get_logger

logger = get_logger(__name__)


def create_database_if_not_exists():
    """
    Connects to the default 'postgres' DB using psycopg2 and creates the target DB
    if it doesn't exist.
    """
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname="postgres",  # connect to default postgres DB to create new DB
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        logger.info("=== Connected to master postgres DB to check/create target DB ===")

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (settings.POSTGRES_DB,))
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE DATABASE {settings.POSTGRES_DB};")
            logger.info(f"=== Database {settings.POSTGRES_DB} created successfully. ===")
        else:
            logger.info(f"=== Database {settings.POSTGRES_DB} already exists, skipping creation. ===")

        cur.close()
        conn.close()
        logger.info("=== Create_db connection closed successfully! ===")

    except Exception as e:
        logger.error(f"=== Error while creating/checking DB: {e} ===")
        raise


def get_sqlalchemy_engine():
    """
    Returns an SQLAlchemy engine for the target DB.
    """
    # Build connection string
    user = settings.POSTGRES_USER
    password = settings.POSTGRES_PASSWORD
    host = settings.POSTGRES_HOST
    port = settings.POSTGRES_PORT
    db = settings.POSTGRES_DB

    engine_url = f"{settings.SQLALCHEMY_DRIVER}://{user}:{password}@{host}:{port}/{db}"
    try:
        engine = create_engine(engine_url, pool_pre_ping=True)
        logger.info(f"=== Successfully created SQLAlchemy engine for {db} ===")
        return engine
    except Exception as e:
        logger.error(f"=== Error creating SQLAlchemy engine for {db}: {e} ===")
        raise


def create_table_if_not_exists(engine, table_name="crypto_data"):
    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id VARCHAR(100),
        symbol VARCHAR(50),
        name VARCHAR(150),
        current_price DOUBLE PRECISION,
        market_cap DOUBLE PRECISION,
        price_change_percentage_24h DOUBLE PRECISION,
        ath DOUBLE PRECISION,
        atl DOUBLE PRECISION,
        time_stamp TIMESTAMP
    );
    """
    try:
        with engine.begin() as conn:
            conn.execute(text(create_table_sql))
        logger.info("=== Succesfully Created Table! ===")
    except Exception as e:
        logger.error(f"=== Error creating table: {e} ===")
        raise


def upsert_daily_data(engine, df, table_name="crypto_data"):
    """
    Deletes any rows for today's date and appends the new DataFrame.
    """
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    try:
        # check if today's data exists
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name} WHERE DATE(time_stamp) = :today"), {"today": today})
            today_count = result.scalar()
        if today_count and today_count > 0:
            logger.info(f"=== Found {today_count} records for {today}. Deleting old data for today ===")
            with engine.begin() as del_conn:
                del_conn.execute(text(f"DELETE FROM {table_name} WHERE DATE(time_stamp) = :today"), {"today": today})
            logger.info("=== Old records for today deleted. Now inserting fresh data... ===")

        # append new data
        # pandas to_sql requires a DBAPI compatible engine
        df.to_sql(name=table_name, con=engine, if_exists="append", index=False)
        logger.info(f"=== New data inserted for {today}. ===")
    except Exception as e:
        logger.error(f"=== Error inserting or updating data: {e} ===")
        raise
