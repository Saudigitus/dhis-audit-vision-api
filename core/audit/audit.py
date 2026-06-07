import os
from core.dhis2.dhis2_helpers import get_audit_sql_view_data, retrieve_audit_sql_view_data
from core.utils.utils import get_since, save_since, format_timestamp
from core.common.constants import constants
from core.audit.audit_helpers import save_audit_json
from core.db.session import SessionLocal
from core.config import settings


SERVER_DHIS2_URL = settings.SERVER_DHIS2_URL
SERVER_DHIS2_AUTH = settings.SERVER_DHIS2_AUTH
SQL_VIEW_ID = settings.SQL_VIEW_ID
DATA_BASE_DIR = settings.DATA_BASE_DIR
OFFSET_HOURS = settings.OFFSET_HOURS


class AuditProcess:
    def __init__(self):
        pass

    def run(self):
        print("Running the audit process...")
        os.makedirs(DATA_BASE_DIR, exist_ok=True)

        try:
            since = get_since()
            current_since = format_timestamp(since)
            server = {
                "url": SERVER_DHIS2_URL,
                "auth": SERVER_DHIS2_AUTH,
                "authType": constants.BASIC
            }
            audit_data = get_audit_sql_view_data(server, SQL_VIEW_ID, current_since, OFFSET_HOURS)

            with SessionLocal() as db:
                save_audit_json(db=db, payload=audit_data)
            save_since()
            print("Audit process completed successfully.")
        except Exception as e:
            print(f"Error during audit process: {e}")
            raise e

    def automatic_run(self, sql_view_id: str, resource_uid: str = None, created_at: str = None, offset_hours: int = OFFSET_HOURS):
        print("Running the automatic audit process...")
        os.makedirs(DATA_BASE_DIR, exist_ok=True)

        try:
            if not created_at or not sql_view_id or not resource_uid:
                raise ValueError("created_at, sql_view_id, and resource_uid parameters are required for automatic_run method")

            current_created_at = format_timestamp(created_at)

            server = {
                "url": SERVER_DHIS2_URL,
                "auth": SERVER_DHIS2_AUTH,
                "authType": constants.BASIC
            }
            audit_data = retrieve_audit_sql_view_data(server, sql_view_id, resource_uid, current_created_at, offset_hours)

            with SessionLocal() as db:
                save_audit_json(db=db, payload=audit_data)
            save_since()
            print("Automatic audit process completed successfully.")
        except Exception as e:
            print(f"Error during automatic audit process: {e}")
            raise e
