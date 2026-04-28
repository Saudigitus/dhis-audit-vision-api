from core.schemas.schemas import AuditObjectCreate, AuditObjectRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from fastapi import Depends, APIRouter
from core.common.generics.crud_base import CRUDBase
from core.models.models import AuditObject
from fastapi import Request
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User
from datetime import datetime


router = APIRouter()

audit_crud = CRUDBase[AuditObject, AuditObjectCreate, AuditObjectRead](AuditObject)


@router.post("/create/", response_model=AuditObjectRead)
def upsert_audit_object(payload: AuditObjectCreate, db: Session = Depends(get_db)):
    return audit_crud.create(db, payload_in=payload)


@router.get("/{id}", response_model=AuditObjectRead)
def get_audit_object(id: str, db: Session = Depends(get_db)):
    return audit_crud.get(db, id=id)


# @router.get("")
# def get_audit_objects(request: Request, page: int = 1, pageSize: int = 50, db: Session = Depends(get_db)):
#     # Grab all query params except pagination ones
#     excluded = {"page", "pageSize"}
#     filters = {k: v for k, v in request.query_params.items() if k not in excluded}
#     result = audit_crud.get_all(db, page=page, pageSize=pageSize, filters=filters)
#     return {"pager": result["pager"], "auditObjects": result["data"]}

@router.get("")
def get_audit_objects(request: Request, page: int = 1, pageSize: int = 50, db: Session = Depends(get_db)):
    excluded = {"page", "pageSize"}
    filters = {k: v for k, v in request.query_params.items() if k not in excluded}
    result = audit_crud.get_all(db, page=page, pageSize=pageSize, filters=filters)
    data = sorted(result["data"], key=lambda x: x.created_at, reverse=True)    
    return {"pager": result["pager"], "auditObjects": data}


@router.delete("/{id}")
def delete_audit_object(id: str, db: Session = Depends(get_db)):
    audit_crud.delete(db, id=id)
    return {"message": "audit object deleted"}
