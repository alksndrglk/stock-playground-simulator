import os
import yaml
import pathlib

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.web.config import DatabaseConfig
from app.store.database.gino import db

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
BASE_DIR = pathlib.Path(__file__).parent.parent

if os.environ.get("CONFIGPATH"):
    config_path = BASE_DIR / os.environ["CONFIGPATH"]
else:
    config_path = BASE_DIR / "config" / "config.yml"

with open(config_path) as config:
    raw_config = yaml.safe_load(config)
    app_config = DatabaseConfig(**raw_config.get("database", {}))


def set_sqlalshemy_url(host: str, db: str, user: str, pasw: str, port):
    config.set_main_option(
        "sqlalchemy.url", f"postgres://{user}:{pasw}@{host}:{port}/{db}"
    )


config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = db

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    set_sqlalshemy_url(
        app_config.host,
        app_config.database,
        app_config.user,
        app_config.password,
        app_config.port,
    )
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    set_sqlalshemy_url(
        app_config.host,
        app_config.database,
        app_config.user,
        app_config.password,
        app_config.port,
    )
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
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
