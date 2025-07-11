from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Added: Make Alembic use proper config class directly
import os
from dotenv import load_dotenv
load_dotenv()

# import our debug util
from app.utils.debug import debug_config

from app.core.config import DevConfig, ProdConfig, TestConfig, config_map

from app.core.db_base import Base  # Import SQLAlchemy Base
from app.core.models import User
from app.modules.tasks.models import Task

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
# Commented out: target_metadata = None
# Added:
# target_metadata needs to be defined before the functions that use it
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Get config & set the database URL
env = os.environ.get('APP_ENV', 'dev')
config_class = config_map[env]

# Debug print for Alembic migrations
debug_config(env, config_class)
print(f"[ALEMBIC] Using database: {config_class.SQLALCHEMY_DATABASE_URI}")

config.set_main_option('sqlalchemy.url', config_class.SQLALCHEMY_DATABASE_URI)


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
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
