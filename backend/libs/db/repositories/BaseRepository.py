from contextlib import contextmanager
from functools import wraps
from typing import Callable, Dict, Generic, Type, TypeVar, Any
from sqlalchemy.orm import Session
from libs.db.common import get_session, session_context_var


class TransactionalMetaclass(type):
    def __new__(cls, name: str, bases: tuple, attrs: Dict[str, Any]) -> Type:
        cls.apply_transactional_wrapper(attrs)
        new_class = super().__new__(cls, name, bases, attrs)
        return new_class

    @classmethod
    def apply_transactional_wrapper(cls, attrs: Dict[str, Any]) -> None:
        transactional_prefixes = (
            "find",
            "create",
            "delete",
        )

        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and any(
                attr_name.startswith(prefix) for prefix in transactional_prefixes
            ):
                attrs[attr_name] = cls.add_transactional(attr_value)

    @classmethod
    def add_transactional(cls, func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with transaction():
                return func(*args, **kwargs)

        return wrapper


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType], TransactionalMetaclass):
    @property
    def session(self) -> Session:
        return session_context_var.get()

    def create(self, instance: ModelType) -> ModelType:
        self.session.add(instance)
        self.session.flush()
        self.session.refresh(instance)
        return instance

    def update(self, instance: ModelType, data: Dict[str, Any]) -> ModelType:
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
            else:
                raise AttributeError(
                    f"{type(instance).__name__} has no attribute '{key}'"
                )

        self.session.flush()
        return instance

    def delete(self, data: ModelType) -> None:
        self.session.delete(data)
        self.session.flush()


@contextmanager
def transaction():
    session = session_context_var.get()
    if session is None:
        session = get_session()
        session_context_var.set(session)

    is_nested = session.in_transaction()

    if is_nested:
        savepoint = session.begin_nested()
        try:
            yield savepoint
        except Exception:
            savepoint.rollback()
        raise
    else:
        try:
            session.begin()
            yield session
            session.commit()
            session.close()

        except Exception:
            session.rollback()
            session.close()

        finally:
            session_context_var.set(None)