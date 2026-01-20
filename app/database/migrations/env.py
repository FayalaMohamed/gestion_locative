"""Alembic environment configuration"""
from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import pool, engine_from_config
from sqlalchemy.engine import Connection

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from alembic.runtime.context import Context
from alembic.script import ScriptDirectory

from app.models.entities import Base
from app.utils.config import Config


def get_database_url() -> str:
    """Get database URL from configuration"""
    config = Config.get_instance()
    db_config = config.get('database') or {}
    path = db_config.get('path', 'data/gestion_locative.db')
    
    if not path.startswith(('sqlite:///', 'postgresql://')):
        path = f"sqlite:///{path}"
    
    return path


def run_migrations_offline() -> None:
    """Run migrations in offline mode (without database connection)"""
    url = get_database_url()
    
    # For offline mode, we use a dummy URL
    context = Context(
        script=ScriptDirectory.from_config(
            Path(__file__).parent / 'alembic.ini'
        ),
        as_sql=False,
        starting_rev=None,
        destination_rev='head',
        opts={
            'compare_type': True,
            'compare_server_default': True,
            'render_item': Base.metadata._render_items,
        }
    )
    
    # Configure logging
    fileConfig(
        Path(__file__).parent / 'alembic.ini',
        disable_existing_loggers=False
    )


def run_migrations_online() -> None:
    """Run migrations in online mode (with database connection)"""
    url = get_database_url()
    
    connectable = engine_from_config(
        {"sqlalchemy.url": url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context = Context(
            script=ScriptDirectory.from_config(
                Path(__file__).parent / 'alembic.ini'
            ),
            as_sql=False,
            starting_rev=None,
            destination_rev='head',
            connection=connection,
            opts={
                'compare_type': True,
                'compare_server_default': True,
                'render_item': Base.metadata._render_items,
            }
        )
        
        context.run_migrations()


if __name__ == "__main__":
    # Check if offline mode is requested
    offline = "--offline" in sys.argv
    
    if offline:
        run_migrations_offline()
    else:
        run_migrations_online()
