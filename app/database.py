from logging import getLogger
from typing import Mapping
from uuid import uuid4

from asyncpg import Connection
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.settings import db_settings, server_settings

log = getLogger()


class UniqueStmtConnection(Connection):
    """
    Connection class where uniq_id really unique.
    """

    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


def build_connect_args(settings) -> Mapping:
    connect_args = {}
    if settings.statement_cache_size == 0:
        connect_args = {
            "statement_cache_size": settings.statement_cache_size,
            "prepared_statement_cache_size": settings.statement_cache_size,
            "connection_class": UniqueStmtConnection,
        }
    return connect_args


def _get_engine(settings, debug: bool = False) -> Engine:
    """
    Retrieve database engine.
    """

    return create_async_engine(
        settings.dsn,
        echo=debug,
        connect_args=build_connect_args(settings),
    )


def _get_async_session(settings, debug: bool = False):
    """
    Retrieves db session object.
    """

    engine = _get_engine(settings, debug)
    return sessionmaker(
        bind=engine, class_=AsyncSession, autocommit=False, autoflush=False, expire_on_commit=False
    )


def get_db_session_dependence(settings, debug: bool = False):
    """
    Func which u can use in Depends()
    """

    async_session = _get_async_session(settings, debug)

    async def get_db_session() -> AsyncSession:
        """
        Create new db session and guarantees that it will be closed.
        """
        async with async_session() as db:
            yield db

    return get_db_session


get_async_session = get_db_session_dependence(db_settings, server_settings.debug)

