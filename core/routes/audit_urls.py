from fastapi import APIRouter, Depends, Query, Request, HTTPException
from core.schemas.schemas import AuditCreate, AuditRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from core.common.generics.crud_base import CRUDBase
from core.models.models import Audit
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User
from core.audit.audit_crud import AuditCRUD as CustomAuditCRUD
from core.common.enums.metadata_type import MetadataType
from core.audit.service import get_latest_audits_for_metadata

MAX_PAGE_SIZE = 100
AUDIT_FILTER_FIELDS = {"auditType", "auditScope", "klass", "createdBy", "uid", "code"}

router = APIRouter()

audit_crud = CRUDBase[Audit, AuditCreate, AuditRead](Audit)


@router.post("/create/", response_model=AuditRead)
def upsert_audit(payload: AuditCreate, db: Session = Depends(get_db), _: User = Depends(require_superuser)):
    return audit_crud.create(db, payload_in=payload)


@router.get("/{id}", response_model=AuditRead)
def get_audit(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
    unknown_filters = set(request.query_params.keys()) - excluded - AUDIT_FILTER_FIELDS
    if unknown_filters:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported filter parameter(s): {', '.join(sorted(unknown_filters))}",
        )
    filters = {k: v for k, v in request.query_params.items() if k not in excluded}
    custom_crud = CustomAuditCRUD(Audit)
    result = custom_crud.get_latest_per_uid(db, page=page, pageSize=pageSize, filters=filters)
    return result


@router.delete("/{id}")
def delete_audit(id: str, db: Session = Depends(get_db), _: User = Depends(require_superuser)):
    audit_crud.delete(db, id=id)
    return {"message": "audit deleted"}


@router.get("/metadata/{id}")
def get_audit_by_program_and_dataset_id(
    request: Request,
    id: str,
    type: MetadataType = Query(..., description="PROGRAM ou DATASET"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(50, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    return get_latest_audits_for_metadata(db, id, type, page, pageSize)
