from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from core.auth.dependencies import get_current_user
from core.auth.models import User
from pydantic import BaseModel, Field
from datetime import datetime
from core.audit.service import extract_resource_uid_from_event_path, process_dhis2_event_safe

router = APIRouter()


class Dhis2EventWebhook(BaseModel):
    path: str
    created_at: datetime = Field(alias="createdAt")


@router.post("/dhis2/event", status_code=status.HTTP_202_ACCEPTED)
async def receive_dhis2_event_webhook(
    payload: Dhis2EventWebhook,
    background_tasks: BackgroundTasks,
    _: User = Depends(get_current_user),
):
    """
    Webhook endpoint to receive events from DHIS2.
    """
    try:
        resource_uid = extract_resource_uid_from_event_path(payload.path)
        background_tasks.add_task(process_dhis2_event_safe, resource_uid, payload.created_at)

        return {
            "status": "accepted",
            "message": "Webhook received and queued for processing"
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process webhook")
