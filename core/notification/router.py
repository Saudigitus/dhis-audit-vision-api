from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from core.db.dependencies import get_db
from core.common.generics.crud_base import CRUDBase
from core.notification.schemas import NotificationConfigCreate, NotificationConfigRead
from core.notification.models import NotificationConfig
from core.auth.dependencies import get_current_user, require_superuser

router = APIRouter(dependencies=[Depends(get_current_user)])
notification_crud = CRUDBase[NotificationConfig, NotificationConfigCreate, NotificationConfigRead](NotificationConfig)
MAX_PAGE_SIZE = 100
NOTIFICATION_FILTER_FIELDS = {"subject", "objectType", "action", "severity"}


@router.post("/create", response_model=NotificationConfigRead)
def save_notification(
    payload: NotificationConfigCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_superuser),
):
    return notification_crud.create(db, payload_in=payload)


@router.get("")
def list_notifications(
    request: Request,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
):
    excluded = {"page", "pageSize"}
    unknown_filters = set(request.query_params.keys()) - excluded - NOTIFICATION_FILTER_FIELDS
    if unknown_filters:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported filter parameter(s): {', '.join(sorted(unknown_filters))}",
        )
    filters = {k: v for k, v in request.query_params.items() if k not in excluded}
    result = notification_crud.get_all(db,  page=page, pageSize=pageSize, filters=filters)
    data = sorted(result["data"], key=lambda x: x.created_at, reverse=True)
    return {"pager": result["pager"], "notifications": data}


@router.get("/{id}", response_model=NotificationConfigRead)
def get_config(request: Request, id: str, db: Session = Depends(get_db)):
    return notification_crud.get(db, id=id)


@router.delete("/{id}", status_code=204)
def remove_config(
    request: Request,
    id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_superuser),
):
    notification_crud.delete(db, id=id)
    return {"message": "Notification config deleted"}
