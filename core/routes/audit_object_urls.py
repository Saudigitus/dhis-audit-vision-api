from core.schemas.schemas import AuditObjectCreate, AuditObjectRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from fastapi import Depends, APIRouter, HTTPException, Query
from core.common.generics.crud_base import CRUDBase
from core.models.models import AuditObject
from fastapi import Request
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User


router = APIRouter()

audit_crud = CRUDBase[AuditObject, AuditObjectCreate, AuditObjectRead](AuditObject)
MAX_PAGE_SIZE = 100
AUDIT_OBJECT_FILTER_FIELDS = {"auditId", "objectId", "auditScope", "auditType"}


@router.post("/create/", response_model=AuditObjectRead)
def upsert_audit_object(payload: AuditObjectCreate, db: Session = Depends(get_db), _: User = Depends(require_superuser)):
    return audit_crud.create(db, payload_in=payload)


@router.get("/{id}", response_model=AuditObjectRead)
def get_audit_object(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return audit_crud.get(db, id=id)


@router.get("")
def get_audit_objects(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    excluded = {"page", "pageSize"}
    unknown_filters = set(request.query_params.keys()) - excluded - AUDIT_OBJECT_FILTER_FIELDS
    if unknown_filters:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported filter parameter(s): {', '.join(sorted(unknown_filters))}",
        )
    filters = {k: v for k, v in request.query_params.items() if k not in excluded}
    result = audit_crud.get_all(db, page=page, pageSize=pageSize, filters=filters, order_by="created_at")
    return {"pager": result["pager"], "auditObjects": result["data"]}


@router.delete("/{id}")
def delete_audit_object(id: str, db: Session = Depends(get_db), _: User = Depends(require_superuser)):
    audit_crud.delete(db, id=id)
    return {"message": "audit object deleted"}
