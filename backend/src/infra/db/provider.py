# ruff: noqa: PLR6301
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import NewType

from dishka import BaseScope, Component, Provider, Scope, provide
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import DBConfig

RWDBEngine = NewType("RWDBEngine", AsyncEngine)
RODBEngine = NewType("RODBEngine", AsyncEngine)

RWSessionFactory = NewType(
    "RWSessionFactory",
    async_sessionmaker[AsyncSession],
)
ROSessionFactory = NewType(
    "ROSessionFactory",
    async_sessionmaker[AsyncSession],
)


@dataclass(frozen=True, slots=True)
class DatabaseEngines:
    rw: AsyncEngine
    ro: AsyncEngine


class DatabaseProvider(Provider):
    def __init__(
        self,
        db_config: DBConfig,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.db_config = db_config

    @provide(scope=Scope.APP)
    async def db_engines(self) -> AsyncIterator[DatabaseEngines]:
        rw_engine = create_async_engine(
            self.db_config.RW_DATABASE_URL,
            echo=False,
            pool_size=7,
            max_overflow=20,
            pool_pre_ping=True,
        )
        ro_engine = create_async_engine(
            self.db_config.RO_DATABASE_URL,
            echo=False,
            pool_size=7,
            max_overflow=20,
            pool_pre_ping=True,
        )
        SQLAlchemyInstrumentor().instrument(
            engines=[rw_engine.sync_engine, ro_engine.sync_engine],
        )
        try:
            yield DatabaseEngines(rw=rw_engine, ro=ro_engine)
        finally:
            await rw_engine.dispose()
            await ro_engine.dispose()

    @provide(scope=Scope.APP)
    def rw_db_engine(self, engines: DatabaseEngines) -> RWDBEngine:
        return RWDBEngine(engines.rw)

    @provide(scope=Scope.APP)
    def ro_db_engine(self, engines: DatabaseEngines) -> RODBEngine:
        return RODBEngine(engines.ro)

    @provide(scope=Scope.APP)
    def rw_session_factory(
        self,
        engine: RWDBEngine,
    ) -> RWSessionFactory:
        factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
        return RWSessionFactory(factory)

    @provide(scope=Scope.APP)
    def ro_session_factory(
        self,
        engine: RODBEngine,
    ) -> ROSessionFactory:
        factory = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
        )
        return ROSessionFactory(factory)
