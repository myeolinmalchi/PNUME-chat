from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from contextvars import ContextVar
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv
import os

load_dotenv()

N_DIM = 1024
Base = declarative_base()

session_context_var: ContextVar = ContextVar("db_session", default=None)

_engine = None
_Session = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        db_type = "postgresql"
        user = os.environ.get("DB_USER")
        pw = os.environ.get("DB_PASSWORD")
        host = os.environ.get("DB_HOST")
        dbname = os.environ.get("DB_NAME")

        _engine = create_engine(f"{db_type}://{user}:{pw}@{host}/{dbname}")

    return _engine


def get_session() -> Session:
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), expire_on_commit=False)

    return _Session()