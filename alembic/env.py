"""Connects Alembic migrations to our Flask app config
1. load_dotenv() loads environment variables
2. get_config() returns the appropriate config class (Dev/Prod/Test)
3. We extract SQLALCHEMY_DATABASE_URI and inject it into Alembic's config
4. Import all models so autogenerate can detect schema changes
"""

from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool
from alembic import context

load_dotenv()  # BEFORE importing+invoking get_config()

from app.config import get_config

# Import all models so autogenerate can detect schema changes
from app._infra.db_base import Base  # Import SQLAlchemy Base
from app.api.models import *
from app.modules.auth.models import *
from app.modules.groceries.models import *
from app.modules.habits.models import *
from app.modules.metrics.models import *
from app.modules.tasks.models import *
from app.modules.time_tracking.models import *


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# inject our db uri based on actual config class
config.set_main_option(
    "sqlalchemy.url",  # Alembic's config key (don't change this)
    get_config().SQLALCHEMY_DATABASE_URI,
)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# ORIGINAL: target_metadata = None
# Added: target_metadata needs to be defined before the functions that use it
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
