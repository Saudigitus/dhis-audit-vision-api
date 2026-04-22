from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

from core.config import settings
from core.db.base import Base
from core.auth import models  # ensure models are imported

# 🔥 ensure .env is loaded
load_dotenv()

config = context.config

# 🔥 override DB URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Debug (remove later)
print("Using DB:", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
