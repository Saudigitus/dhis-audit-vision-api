from core.common.enums.audit_enums import AuditType, AuditScope
from core.utils.id_generator import generate_custom_id
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy import Column, String, Enum, Text
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from core.db.base import Base


class GenericModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class Audit(GenericModel):
    __tablename__ = "audit"

    id = Column(String(11), primary_key=True, default=generate_custom_id)

    audit_type = Column(Enum(AuditType), nullable=False)
    audit_scope = Column(Enum(AuditScope), nullable=False)
    klass = Column(Text, nullable=False)
    attributes = Column(JSONB, nullable=True)
    data = Column(BYTEA, nullable=True)
    created_by = Column(String, nullable=False)
    uid = Column(String, nullable=True)
    code = Column(String, nullable=True)
