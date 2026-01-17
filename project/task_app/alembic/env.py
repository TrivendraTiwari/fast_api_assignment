# import sys
# import os
# from logging.config import fileConfig
# from sqlalchemy import create_engine,engine_from_config, pool
# from alembic import context

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# from app.db.models import Base 

# config = context.config

# fileConfig(config.config_file_name)
# target_metadata = Base.metadata

# # ----------------------------
# # Offline migration
# # ----------------------------
# def run_migrations_offline():
#     # url = config.get_main_option("sqlalchemy.url")
#     url = "postgresql+psycopg2://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True
#     )
#     with context.begin_transaction():
#         context.run_migrations()

# # ----------------------------
# # Online migration
# # ----------------------------
# def run_migrations_online():
#     DATABASE_URL = "postgresql+psycopg2://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"
#     connectable = create_engine(
#         DATABASE_URL,
#         poolclass=pool.NullPool
#     )

#     with connectable.connect() as connection:
#         context.configure(connection=connection, target_metadata=target_metadata)
#         with context.begin_transaction():
#             context.run_migrations()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()



import sys
from pathlib import Path
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlalchemy import create_engine


# ---------------- PATH FIX ----------------
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

# ---------------- CONFIG ----------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------- MODELS ----------------
from task_app.app.database_setup.models import Base
target_metadata = Base.metadata


# ----------------------------
# Function to ignore partition tables
# ----------------------------
def include_object(object, name, type_, reflected, compare_to):
    # Ignore all tasks partitions
    if type_ == "table" and name.startswith("tasks_p"):
        return False
    return True

# ----------------------------
# Offline migration
# ----------------------------
def run_migrations_offline():
    url = "postgresql+psycopg2://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object
    )
    with context.begin_transaction():
        context.run_migrations()

# ----------------------------
# Online migration
# ----------------------------
def run_migrations_online():
    DATABASE_URL = "postgresql+psycopg2://fastapi_user:fastapi_pass@localhost:5432/fastapi_db"
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
