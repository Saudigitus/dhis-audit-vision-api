import json
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from core.models.models import Audit, AuditObject
from core.common.enums.audit_enums import AuditType, AuditScope
from core.dhis2.dhis2_helpers import get_resouce_object_data, get_resources_mapping
import os
from dotenv import load_dotenv
from core.common.constants import constants
from core.utils.id_generator import generate_custom_id


load_dotenv()

SERVER_DHIS2_URL = os.getenv("SERVER_DHIS2_URL", "https://play.im.dhis2.org/stable-2-41-8")
SERVER_DHIS2_AUTH = os.getenv("SERVER_DHIS2_AUTH", "YWRtaW46ZGlzdHJpY3Q=")
BATCH_SIZE = 50


def chunk_list(data: List, size: int):
    """Yield successive chunks from list"""
    for i in range(0, len(data), size):
        yield data[i:i + size]


def parse_audit_row(headers: List[str], row: List) -> Audit:
    """Convert a row into an Audit model"""
    record = dict(zip(headers, row))

    # Parse attributes JSON safely
    attributes = None
    if record.get("attributes"):
        try:
            attributes = json.loads(record["attributes"])
        except Exception:
            attributes = None

    # Parse datetime
    created_at = None
    if record.get("createdat"):
        try:
            created_at = datetime.strptime(record["createdat"], "%Y-%m-%d %H:%M:%S.%f")
        except Exception:
            created_at = None

    audit = Audit(
        id=generate_custom_id(),
        auditType=AuditType(record["audittype"]),
        auditScope=AuditScope(record["auditscope"]),
        klass=record["klass"],
        attributes=attributes,
        data=None,  # ignore invalid Java byte references
        createdBy=record["createdby"],
        uid=record.get("uid"),
        code=record.get("code"),
    )

    if created_at:
        audit.created_at = created_at

    return audit


def save_audit_json(db: Session, payload: Dict,  batch_size: int = BATCH_SIZE) -> Dict:
    """
    Generic function to save audit data from JSON into DB.
    Args:
        db: SQLAlchemy session
        payload: JSON payload (audit_data.json)
        batch_size: number of records per batch

    Returns:
        dict with stats
    """

    headers = [h["name"] for h in payload["listGrid"]["headers"]]
    rows = payload["listGrid"]["rows"]

    total, success, failed = len(rows), 0, 0

    for chunk in chunk_list(rows, batch_size):
        batch_objects = []

        for row in chunk:
            try:
                audit = parse_audit_row(headers, row)
                batch_objects.append(audit)
            except Exception:
                failed += 1

        try:
            if batch_objects:
                db.bulk_save_objects(batch_objects)
                db.commit()
                audit_objects = create_audit_objects_from_audit(batch_objects)
                saved_data = save_audit_objects(db, audit_objects)
                success += len(batch_objects)
        except SQLAlchemyError as e:
            db.rollback()
            failed += len(batch_objects)
            print("Database error:", str(e))
            if hasattr(e, "orig"):
                print("DB driver error:", e.orig)
            raise e
        
    print(f"Finished saving audits. Total: {total}, Success: {success}, Failed: {failed}")

    return {
        "total": total,
        "success": success,
        "failed": failed
    }


def create_audit_objects_from_audit(audits: list[Audit]) -> List[AuditObject]:
    """Create AuditObject models from an Audit model"""
    print("Creating AuditObjects from Audits...")
    mapping = get_resources_mapping()

    try:
        audit_objects = []
        for audit in audits:
            if audit.klass:
                resource_id = audit.uid
                resource_endpoint = mapping.get(audit.klass).get("endpoint")
                server = {"url": SERVER_DHIS2_URL, "auth": SERVER_DHIS2_AUTH,  "authType": constants.BASIC}
                if resource_id:
                    object_data = get_resouce_object_data(server, resource_endpoint, resource_id)
                    audit_object = AuditObject(auditId=audit.id, objectId=resource_id, objectData=object_data)
                    audit_objects.append(audit_object)
        return audit_objects
    except Exception as e:
        print(f"Error creating AuditObjects")
        raise e


def save_audit_objects(db: Session, audit_objects: List[AuditObject], batch_size: int = BATCH_SIZE) -> Dict:

    total, success, failed = len(audit_objects), 0, 0

    for chunk in chunk_list(audit_objects, batch_size):
        try:
            db.bulk_save_objects(chunk)
            db.commit()
            print(f"Saved batch of {len(chunk)} AuditObjects")
            success += len(chunk)

        except SQLAlchemyError as e:
            db.rollback()
            failed += len(chunk)
            print("Database error:", str(e))
            if hasattr(e, "orig"):
                print("DB driver error:", e.orig)
            raise e
    print(f"Finished saving AuditObjects. Total: {total}, Success: {success}, Failed: {failed}")
    return {
        "total": total,
        "success": success,
        "failed": failed
    }
