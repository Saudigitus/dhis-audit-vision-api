from core.schemas.schemas import AuditCreate, AuditRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from fastapi import Depends, APIRouter
from core.common.generics.crud_base import CRUDBase
from core.models.models import Audit
from fastapi import Request
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User
from core.audit.audit_crud import AuditCRUD as  CustomAuditCRUD

router = APIRouter()

audit_crud = CRUDBase[Audit, AuditCreate, AuditRead](Audit)


@router.post("/create/", response_model=AuditRead)
def upsert_audit(payload: AuditCreate, db: Session = Depends(get_db)):
    return audit_crud.create(db, payload_in=payload)


@router.get("/{id}", response_model=AuditRead)
def get_audit(id: str, db: Session = Depends(get_db)):
    return audit_crud.get(db, id=id)


@router.get("")
def get_audit_objects(request: Request, page: int = 1, pageSize: int = 50, db: Session = Depends(get_db)):
    # Grab all query params except pagination ones
    excluded = {"page", "pageSize"}
    filters = {k: v for k, v in request.query_params.items() if k not in excluded}
    custom_crud = CustomAuditCRUD(Audit)
    result = custom_crud.get_latest_per_uid(db, page=page, pageSize=pageSize, filters=filters)
    return result


@router.delete("/{id}")
def delete_audit(id: str, db: Session = Depends(get_db)):
    audit_crud.delete(db, id=id)
    return {"message": "audit deleted"}
