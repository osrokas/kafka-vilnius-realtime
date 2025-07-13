import os

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from geoalchemy2 import alembic_helpers

from alembic import context

from dotenv import load_dotenv

import db.models as models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

if os.path.exists(".env"):
    load_dotenv(".env", override=True)

section = config.config_ini_section
config.set_section_option(section, "POSTGRES_USER", os.environ.get("POSTGRES_USER"))
config.set_section_option(section, "POSTGRES_PASSWORD", os.environ.get("POSTGRES_PASSWORD"))
config.set_section_option(section, "POSTGRES_DB", os.environ.get("POSTGRES_DB"))
config.set_section_option(section, "POSTGRES_HOST", os.environ.get("POSTGRES_HOST"))

target_metadata = models.Base.metadata


def include_name(name, type_, parent_names):
    if type_ == "table":
        return name in target_metadata.tables
    else:
        return True


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(name, type_, parent_names):
    excluded_schemas = ["tiger", "tiger_data", "topology"]

    # Filter out objects in excluded schemas
    if type_ == "schema":
        return name in excluded_schemas
    return True


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
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=alembic_helpers.writer,
        render_item=alembic_helpers.render_item,
        target_metadata=target_metadata,
        include_name=include_name,
        include_schemas=False,
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
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=alembic_helpers.writer,
            render_item=alembic_helpers.render_item,
            include_name=include_name,
            include_schemas=False,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
