from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from core.common.enums.audit_enums import AuditType, AuditScope


# ========================
# Base Schemas
# ========================

class BaseCreateSchema(BaseModel):
    id: Optional[str] = None
    model_config = ConfigDict(extra="forbid")


class BaseReadSchema(BaseModel):
    id: str
    createdAt: datetime = Field(alias="created_at")
    updatedAt: datetime = Field(alias="updated_at")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ========================
# Audit Schemas
# ========================

class AuditBase(BaseModel):
    auditType: AuditType = Field(alias="audit_type")
    auditScope: AuditScope = Field(alias="audit_scope")
    klass: str
    attributes: Optional[Dict] = None
    createdBy: str = Field(alias="created_by")
    uid: Optional[str] = None
    code: Optional[str] = None
    model_config = ConfigDict(populate_by_name=True)


class AuditCreate(AuditBase, BaseCreateSchema):
    pass


class AuditRead(AuditBase, BaseReadSchema):
    pass


# ========================
# AuditObject Schemas
# ========================
class AuditObjectBase(BaseModel):
    auditId: str = Field(alias="audit_id")
    objectId: str = Field(alias="object_id")
    objectData: list | dict = Field(alias="object_data")
    model_config = ConfigDict(populate_by_name=True)


class AuditObjectCreate(AuditObjectBase, BaseCreateSchema):
    pass


class AuditObjectRead(AuditObjectBase, BaseReadSchema):
    pass
