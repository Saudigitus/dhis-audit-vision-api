from core.common.enums.audit_enums import AuditType, AuditScope
from core.utils.id_generator import generate_custom_id
from sqlalchemy.dialects.postgresql import JSONB, BYTEA
from sqlalchemy import Column, String, Enum, Text, JSON
from core.db.base import GenericModel


class Audit(GenericModel):
    __tablename__ = "audit"

    id = Column(String(11), primary_key=True, default=generate_custom_id)

    auditType = Column(Enum(AuditType), nullable=False, index=True)
    auditScope = Column(Enum(AuditScope), nullable=False, index=True)
    klass = Column(Text, nullable=False, index=True)
    attributes = Column(JSONB, nullable=True)
    data = Column(BYTEA, nullable=True)
    createdBy = Column(String, nullable=False, index=True)
    uid = Column(String, nullable=True, index=True)
    code = Column(String, nullable=True, index=True)


class AuditObject(GenericModel):
    __tablename__ = "audit_object"

    id = Column(String(11), primary_key=True, default=generate_custom_id)
    auditId = Column(String(11), nullable=False, index=True)
    objectId = Column(String, nullable=False, index=True)
    objectData = Column(JSON, nullable=False)
    auditScope = Column(Enum(AuditScope), nullable=False, index=True)
    auditType = Column(Enum(AuditType), nullable=False, index=True)
