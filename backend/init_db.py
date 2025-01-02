import os

from sqlalchemy import inspect, create_engine, text
from sqlalchemy.exc import ProgrammingError
from libs.db.common import Base, get_engine
from libs.db.models import Notice

def init_database():
    db_type = "postgresql"
    user = os.environ.get("DB_USER")
    pw = os.environ.get("DB_PASSWORD")
    host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

    engine = create_engine(f"{db_type}://{user}:{pw}@{host}")

    try:
        inspector = inspect(engine)
        databases = inspector.get_schema_names()

        if db_name in databases:
            with engine.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
                conn.execute(text(f"CREATE DATABASE {db_name}"))

        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS vector"))

        Base.metadata.create_all(engine)
    except ProgrammingError as e:
        print(f"Error has been occurred: {e}")


if __name__ == "__main__":
    init_database()
