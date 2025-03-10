from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from contextvars import ContextVar
from dotenv import load_dotenv

load_dotenv()

import os
from sqlalchemy.orm import declarative_base

N_DIM, V_DIM = (1024, 250002)

Base = declarative_base()

session_context_var: ContextVar = ContextVar("db_session", default=None)

_engine = None
_Session = None

from sqlalchemy import Enum

_values_callable = lambda obj: [e.value for e in obj]
SQLEnum = lambda SomeEnum: Enum(SomeEnum, values_callable=_values_callable)


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        db_type = "postgresql"
        user = os.environ.get("DB_USER")
        pw = os.environ.get("DB_PASSWORD")
        host = os.environ.get("DB_HOST")
        db_name = os.environ.get("DB_NAME")

        _engine = create_engine(f"{db_type}://{user}:{pw}@{host}/{db_name}")

    return _engine


def get_session() -> Session:
    global _Session
    if _Session is None:
        _Session = sessionmaker(bind=get_engine(), expire_on_commit=False)

    return _Session()
