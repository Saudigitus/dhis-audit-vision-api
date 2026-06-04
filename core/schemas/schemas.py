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
    createdAt: datetime = Field(alias="createdAt")
    updatedAt: datetime = Field(alias="updatedAt")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ========================
# Audit Schemas
# ========================

class AuditBase(BaseModel):
    auditType: AuditType = Field(alias="auditType")
    auditScope: AuditScope = Field(alias="auditScope")
    klass: str
    attributes: Optional[Dict] = None
    createdBy: str = Field(alias="createdBy")
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
    auditId: str = Field(alias="auditId")
    objectId: str = Field(alias="objectId")
    objectData: list | dict = Field(alias="objectData")
    auditScope: AuditScope = Field(alias="auditScope")
    auditType: AuditType = Field(alias="auditType")
    model_config = ConfigDict(populate_by_name=True)


class AuditObjectCreate(AuditObjectBase, BaseCreateSchema):
    pass


class AuditObjectRead(AuditObjectBase, BaseReadSchema):
    pass
