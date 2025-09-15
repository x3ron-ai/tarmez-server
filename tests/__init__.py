import os
import pytest
from alembic import command
from alembic.config import Config

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    db_url = "sqlite:///./test_db.sqlite3"
    os.environ["DATABASE_URL"] = db_url

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(alembic_cfg, "head")

    yield
