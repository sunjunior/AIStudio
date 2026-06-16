import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker, scoped_session

from . import config


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
        _engine = create_engine(
            f"sqlite:///{config.DB_PATH}",
            echo=False,
            connect_args={"check_same_thread": False},
        )

        @event.listens_for(_engine, "connect")
        def _set_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = scoped_session(sessionmaker(bind=get_engine()))
    return _SessionLocal


def init_db():
    """Create all tables."""
    from .models import ModelRegistry, TrainingTask, EvaluationRecord, PublishedService  # noqa
    Base.metadata.create_all(bind=get_engine())
