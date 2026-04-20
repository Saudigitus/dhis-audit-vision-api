from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BoundBaseClass(Base):
    __abstract__ = True

# Import models package to register all models

from core.models.models import *