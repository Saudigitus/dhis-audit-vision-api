import math
import logging
from datetime import datetime

from fastapi import HTTPException
from requests.exceptions import HTTPError
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.audit.audit import AuditProcess
from core.common.constants import constants
from core.common.enums.metadata_type import MetadataType
from core.config import settings
from core.dhis2.dhis2_helpers import get_dataset_dependants, get_program_dependants
from core.models.models import Audit

logger = logging.getLogger(__name__)


def extract_resource_uid_from_event_path(path: str) -> str:
    path_parts = path.split(".")
    if len(path_parts) < 3:
        raise ValueError("Invalid DHIS2 event path")
    return path_parts[2]


def process_dhis2_event(resource_uid: str, created_at: datetime) -> None:
    created_at_text = created_at.strftime("%Y-%m-%d %H:%M:%S.%f")
    audit_process = AuditProcess()
    audit_process.automatic_run(settings.RETRIEVE_SQL_VIEW_ID, resource_uid, created_at_text)


def process_dhis2_event_safe(resource_uid: str, created_at: datetime) -> None:
    try:
        process_dhis2_event(resource_uid, created_at)
    except Exception:
        logger.exception("Error processing DHIS2 event webhook in background")


def get_related_metadata_ids(metadata_id: str, metadata_type: MetadataType) -> list[str]:
    server = {
        "url": settings.SERVER_DHIS2_URL,
        "auth": settings.SERVER_DHIS2_AUTH,
        "authType": constants.BASIC,
    }

    try:
        if metadata_type == MetadataType.PROGRAM:
            return get_program_dependants(server=server, program_id=metadata_id)
        if metadata_type == MetadataType.DATASET:
            return get_dataset_dependants(server=server, dataset_id=metadata_id)
        raise HTTPException(status_code=400, detail="type inválido. Use PROGRAM ou DATASET.")
    except HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail=f"{metadata_type.value} com id {metadata_id} não encontrado no DHIS2.",
            ) from exc
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar {metadata_type.value} no DHIS2: {str(exc)}",
        ) from exc


def get_latest_audits_for_metadata(
    db: Session,
    metadata_id: str,
    metadata_type: MetadataType,
    page: int,
    page_size: int,
) -> dict:
    ids = get_related_metadata_ids(metadata_id, metadata_type)
    if not ids:
        return {"page": page, "pageSize": page_size, "total": 0, "data": []}

    subquery = (
        db.query(Audit.uid, func.max(Audit.created_at).label("max_date"))
        .filter(Audit.uid.in_(ids))
        .group_by(Audit.uid)
        .subquery()
    )

    query = db.query(Audit).join(
        subquery,
        (Audit.uid == subquery.c.uid) & (Audit.created_at == subquery.c.max_date),
    )

    total = query.count()
    audits = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "pager": {
            "page": page,
            "pageSize": page_size,
            "total": total,
            "pageCount": math.ceil(total / page_size) if total else 0,
        },
        "audits": audits,
    }
