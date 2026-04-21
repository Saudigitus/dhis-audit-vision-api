from core.schemas.schemas import AuditCreate, AuditRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from fastapi import Depends, APIRouter
from core.common.generics.crud_base import CRUDBase
from core.models.models import Audit
from typing import List

router = APIRouter()

audit_crud = CRUDBase[Audit, AuditCreate, AuditRead](Audit)

# Routes


@router.post("/create/", response_model=AuditRead)
def upsert_audit(payload: AuditCreate, db: Session = Depends(get_db)):
    return audit_crud.create(db, payload_in=payload)


@router.get("/{id}", response_model=AuditRead)
def get_audit(id: str, db: Session = Depends(get_db)):
    return audit_crud.get(db, id=id)


@router.get("", response_model=List[AuditRead])
def get_audits(page: int = 1, pageSize: int = 100, db: Session = Depends(get_db)):
    return audit_crud.get_all(db, page=page, pageSize=pageSize)


@router.delete("/{id}")
def delete_audit(id: str, db: Session = Depends(get_db)):
    audit_crud.delete(db, id=id)
    return {"message": "audit deleted"}
