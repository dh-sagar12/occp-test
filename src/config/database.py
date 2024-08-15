import os
import time
from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    configure_mappers,
)
from enum import Enum
import sqlalchemy as sa
from sqlalchemy.exc import OperationalError

pg_user = os.environ["POSTGRES_USER"]
pg_pass = os.environ["POSTGRES_PASSWORD"]
pg_host = os.environ["POSTGRES_HOST"]
pg_port = os.environ["POSTGRES_PORT"]
pg_db = os.environ["POSTGRES_DB"]
pg_schema = os.environ.get("POSTGRES_SCHEMA", "public") 

pg_str = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"

engine = create_engine(pg_str)

if os.environ["STAGE"] == "LOCAL":
    Base = declarative_base(
        type_annotation_map={Enum: sa.Enum(Enum, inherit_schema=True)}
    )
else:
    metadata = MetaData(schema=pg_schema)

    Base = declarative_base(
        metadata=metadata,
        type_annotation_map={Enum: sa.Enum(Enum, inherit_schema=True)},
    )


def create_schema_if_not_exists(engine, schema_name):
    inspector = inspect(engine)
    if schema_name not in inspector.get_schema_names():
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            conn.commit()


def wait_for_db(engine, retries=10, delay=10):
    for i in range(retries):
        try:
            create_schema_if_not_exists(engine, pg_schema)
            break
        except OperationalError:
            if i < retries - 1:
                print(f"Database is not ready yet. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("Max retries reached. Database is still not ready.")
                raise

wait_for_db(engine)

configure_mappers()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
