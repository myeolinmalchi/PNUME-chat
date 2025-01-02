from sqlalchemy.exc import ProgrammingError
from db.common import Base, get_engine
from db.models import *


def init_database():
    """
    db_type = "postgresql"
    user = os.environ.get("DB_USER")
    pw = os.environ.get("DB_PASSWORD")
    host = os.environ.get("DB_HOST")
    db_name = os.environ.get("DB_NAME")

    engine = create_engine(f"{db_type}://{user}:{pw}@{host}/postgres")
    """

    try:
        """
        inspector = inspect(engine)
        databases = inspector.get_schema_names()

        with engine.connect() as conn:
            conn.execute(text(f"SET AUTOCOMMIT = ON;"))
            conn.commit()
            if db_name in databases:
                conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
            conn.execute(text(f"CREATE DATABASE {db_name}"))
        """

        engine = get_engine()
        """
        with engine.connect() as conn:
            conn.execute(text(f"CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        """

        Base.metadata.create_all(engine)
    except ProgrammingError as e:
        print(f"Error has been occurred: {e}")


if __name__ == "__main__":
    init_database()
