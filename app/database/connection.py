"""Database connection and session management module"""
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.models.entities import Base
from app.utils.config import Config


class Database:
    """Database manager for handling SQLAlchemy connection"""
    
    _instance: Optional['Database'] = None
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    
    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self) -> None:
        """Initialize database connection"""
        if self._engine is not None:
            return
            
        config = Config.get_instance()
        db_config = config.get('database') or {}
        
        db_path = db_config.get('path', 'data/gestion_locative.db')
        
        # Create parent directory if needed
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # SQLite connection URL
        database_url = f"sqlite:///{db_path}"
        
        # Create engine
        self._engine = create_engine(
            database_url,
            connect_args={
                'check_same_thread': False,
                'timeout': 30,
            },
            poolclass=StaticPool,
            echo=config.get('app', 'debug', default=False)
        )
        
        # Session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False
        )
        
        # Enable foreign keys for SQLite
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.close()
    
    @property
    def engine(self) -> Engine:
        """Return SQLAlchemy engine"""
        if self._engine is None:
            self.initialize()
        assert self._engine is not None
        return self._engine
    
    @property
    def session_factory(self) -> sessionmaker:
        """Return session factory"""
        if self._session_factory is None:
            self.initialize()
        assert self._session_factory is not None
        return self._session_factory
    
    def create_tables(self) -> None:
        """Create all tables defined in models"""
        Base.metadata.create_all(self.engine)
    
    def drop_tables(self) -> None:
        """Drop all tables (WARNING: data loss)"""
        Base.metadata.drop_all(self.engine)
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager for sessions with automatic commit/rollback"""
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session(self) -> Session:
        """Return a new session (must be closed manually)"""
        return self.session_factory()


def get_database() -> Database:
    """Factory function to get database instance"""
    db = Database()
    db.initialize()
    return db


def init_database() -> Database:
    """Initialize and return database"""
    db = get_database()
    db.create_tables()
    return db
