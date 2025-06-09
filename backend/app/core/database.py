"""
Database configuration and session management for the Men's Circle Management Platform
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional

from ..config import get_settings

# Global engine variables
_main_engine: Optional[object] = None
_credentials_engine: Optional[object] = None
_main_session_local: Optional[object] = None
_credentials_session_local: Optional[object] = None


def get_main_engine():
    """Get or create the main database engine"""
    global _main_engine
    if _main_engine is None:
        settings = get_settings()
        _main_engine = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    return _main_engine


def get_credentials_engine():
    """Get or create the credentials database engine"""
    global _credentials_engine
    if _credentials_engine is None:
        settings = get_settings()
        _credentials_engine = create_async_engine(
            settings.credentials_database_url,
            echo=settings.debug,
            pool_pre_ping=True,
            pool_recycle=300,
        )
    return _credentials_engine


def get_main_session_local():
    """Get or create the main session maker"""
    global _main_session_local
    if _main_session_local is None:
        _main_session_local = async_sessionmaker(
            bind=get_main_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _main_session_local


def get_credentials_session_local():
    """Get or create the credentials session maker"""
    global _credentials_session_local
    if _credentials_session_local is None:
        _credentials_session_local = async_sessionmaker(
            bind=get_credentials_engine(),
            class_=AsyncSession,
            expire_on_commit=False
        )
    return _credentials_session_local


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass


class CredentialsBase(DeclarativeBase):
    """Base class for credentials database models"""
    pass


async def get_main_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get main database session
    
    Yields:
        AsyncSession: Database session for main application data
    """
    session_local = get_main_session_local()
    async with session_local() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_credentials_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get credentials database session
    
    Yields:
        AsyncSession: Database session for credentials data
    """
    session_local = get_credentials_session_local()
    async with session_local() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    main_engine = get_main_engine()
    credentials_engine = get_credentials_engine()
    
    async with main_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with credentials_engine.begin() as conn:
        await conn.run_sync(CredentialsBase.metadata.create_all)


# Compatibility alias for common usage
get_db = get_main_db


async def close_db():
    """Close database connections"""
    global _main_engine, _credentials_engine
    if _main_engine:
        await _main_engine.dispose()
        _main_engine = None
    if _credentials_engine:
        await _credentials_engine.dispose()
        _credentials_engine = None 