import contextlib
from datetime import datetime
from typing import Any, AsyncIterator

from sqlalchemy import MetaData, DateTime, func
from sqlalchemy.orm import Mapped, declared_attr, DeclarativeBase, mapped_column
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


meta = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

class Base(DeclarativeBase):
    metadata=meta
    """
    Base class for SQLAlchemy models with common attributes to stay DRY (Don't Repeat Yourself).

    This class is intended to serve as a base class for SQLAlchemy models.
    It defines common attributes such as table name, creation timestamp,
    and update timestamp that can be inherited by other models, helping you
    to adhere to the DRY (Don't Repeat Yourself) principle.

    Attributes:
        __tablename__ (str): The table name, derived from the class name in lowercase.
        id (str): The unique ID of each record.
        created_on (datetime): The timestamp of when the record was created.
        updated_on (datetime, optional): The timestamp of when the record was last updated.
            Defaults to None until an update occurs.

    Example:
        To create a SQLAlchemy model using this base class:


        class YourModel(Base_):
            # Define additional attributes for your model here.

    """
    # @declared_attr
    # def __tablename__(cls):
    #     # The table name is derived from the class name in lowercase
    #     return cls.__name__.lower()

    # # The unique UUID ID for each record
    # id: Mapped[str] = mapped_column(primary_key=True, default=idgen,index=True)

    # The timestamp for record creation
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # The timestamp for record update, initially None until an update occurs
    updated_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


# https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308
# https://github.com/ThomasAitken/demo-fastapi-async-sqlalchemy/blob/main/backend/app/api/dependencies/core.py
class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

            # closing means the models are removed from memory

sessionmanager = DatabaseSessionManager(str(settings.asyncpg_url), {"echo": settings.echo_sql})


async def get_db_session(): 
    async with sessionmanager.session() as session:
        yield session