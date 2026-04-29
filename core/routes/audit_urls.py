from typing import List
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from enum import Enum
from core.common.constants import constants
from core.schemas.schemas import AuditCreate, AuditRead
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from fastapi import Depends, APIRouter
from core.common.generics.crud_base import CRUDBase
from core.models.models import Audit
from fastapi import Request
from core.auth.dependencies import get_current_user, require_superuser
from core.auth.models import User
from core.audit.audit_crud import AuditCRUD as CustomAuditCRUD
from core.common.enums.metadata_type import MetadataType
from core.dhis2.dhis2_helpers import get_program_dependants, get_dataset_dependants
from dotenv import load_dotenv
import os
from sqlalchemy import func
import math
from requests.exceptions import HTTPError

SERVER_DHIS2_URL = os.getenv("SERVER_DHIS2_URL", "https://play.im.dhis2.org/stable-2-41-8")
SERVER_DHIS2_AUTH = os.getenv("SERVER_DHIS2_AUTH", "YWRtaW46ZGlzdHJpY3Q=")

router = APIRouter()
load_dotenv()

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


@router.get("/metadata/{id}")
def get_audit_by_program_and_dataset_id(request: Request,   id: str, type: MetadataType = Query(..., description="PROGRAM ou DATASET"), page: int = 1, pageSize: int = 50, db: Session = Depends(get_db)):
    server = {"url": SERVER_DHIS2_URL, "auth": SERVER_DHIS2_AUTH, "authType": constants.BASIC}

    try:
        if type == MetadataType.PROGRAM:
            ids = get_program_dependants(server=server, program_id=id)

        elif type == MetadataType.DATASET:
            ids = get_dataset_dependants(server=server, dataset_id=id)

        else:
            raise HTTPException(status_code=400, detail="type inválido. Use PROGRAM ou DATASET.")

    except HTTPError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"{type.value} com id {id} não encontrado no DHIS2.")
        else:
            raise HTTPException(status_code=500, detail=f"Erro ao buscar {type.value} no DHIS2: {str(e)}")

    if not ids:
        return {"page": page, "pageSize": pageSize, "total": 0, "data": []}

    # Step 1: Query latest audit per uid
    subquery = (
        db.query(Audit.uid, func.max(Audit.created_at).label("max_date"))
        .filter(Audit.uid.in_(ids))
        .group_by(Audit.uid)
        .subquery()
    )

    query = (
        db.query(Audit)
        .join(
            subquery,
            (Audit.uid == subquery.c.uid) &
            (Audit.created_at == subquery.c.max_date)
        )
    )

    # Step 2: Pagination
    total = query.count()

    audits = (
        query
        .offset((page - 1) * pageSize)
        .limit(pageSize)
        .all()
    )

    return {
        "pager": {
            "page": page,
            "pageSize": pageSize,
            "total": total,
            "pageCount": math.ceil(total / pageSize) if total else 0
        },
        "audits": audits
    }
