from fastapi import APIRouter, Depends, HTTPException
import logging
from core.auth.dependencies import get_current_user
from core.auth.models import User
from core.audit.audit import AuditProcess
from pydantic import BaseModel, Field
from datetime import datetime
from core.common.config import get_required_env

RETRIEVE_SQL_VIEW_ID = get_required_env("RETRIEVE_SQL_VIEW_ID")

logger = logging.getLogger(__name__)

router = APIRouter()


class Dhis2EventWebhook(BaseModel):
    path: str
    created_at: datetime = Field(alias="createdAt")


@router.post("/dhis2/event")
async def receive_dhis2_event_webhook(
    payload: Dhis2EventWebhook,
    _: User = Depends(get_current_user),
):
    """
    Webhook endpoint to receive events from DHIS2.
    """
    try:
        audit_process = AuditProcess()

        path_parts = payload.path.split(".")
        if len(path_parts) < 3:
            raise HTTPException(status_code=400, detail="Invalid DHIS2 event path")

        resource_uid = path_parts[2]
        created_at = payload.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")

        audit_process.automatic_run(RETRIEVE_SQL_VIEW_ID, resource_uid, created_at)

        return {
            "status": "success",
            "message": "Webhook received successfully"
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Error processing DHIS2 event webhook")
        raise HTTPException(status_code=500, detail="Failed to process webhook")
