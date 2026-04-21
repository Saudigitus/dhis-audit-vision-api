from core.schemas.schemas import AuditObjectCreate, AuditObjectRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from fastapi import Depends, APIRouter
from core.common.generics.crud_base import CRUDBase
from core.models.models import AuditObject
from typing import List

router = APIRouter()

audit_crud = CRUDBase[AuditObject, AuditObjectCreate, AuditObjectRead](AuditObject)

# Routes


@router.post("/create/", response_model=AuditObjectRead)
def upsert_audit_object(payload: AuditObjectCreate, db: Session = Depends(get_db)):
    return audit_crud.create(db, payload_in=payload)


@router.get("/{id}", response_model=AuditObjectRead)
def get_audit_object(id: str, db: Session = Depends(get_db)):
    return audit_crud.get(db, id=id)


@router.get("", response_model=List[AuditObjectRead])
def get_audit_objects(page: int = 1, pageSize: int = 100, db: Session = Depends(get_db)):
    return audit_crud.get_all(db, page=page, pageSize=pageSize)


@router.delete("/{id}")
def delete_audit_object(id: str, db: Session = Depends(get_db)):
    audit_crud.delete(db, id=id)
    return {"message": "audit object deleted"}
