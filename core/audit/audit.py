import os
import json
from dotenv import load_dotenv
from core.dhis2.dhis2_helpers import get_audit_sql_view_data
from core.utils.utils import get_since, save_since
from core.common.constants import constants
from core.audit.audit_helpers import save_audit_json
from core.db.session import SessionLocal

db = SessionLocal()
load_dotenv()


SERVER_DHIS2_URL = os.getenv("SERVER_DHIS2_URL", "https://play.im.dhis2.org/stable-2-41-8")
SERVER_DHIS2_AUTH = os.getenv("SERVER_DHIS2_AUTH", "YWRtaW46ZGlzdHJpY3Q=")
SQL_VIEW_ID = os.getenv("SQL_VIEW_ID", "k7RGz4qMNXk")
DATA_BASE_DIR = os.getenv("DATA_BASE_DIR", "/data")


class AuditProcess:
    def __init__(self):
        pass

    def run(self):
        print("Running the audit process...")
        os.makedirs(DATA_BASE_DIR, exist_ok=True)

        try:
            since = get_since()
            server = {
                "url": SERVER_DHIS2_URL,
                "auth": SERVER_DHIS2_AUTH,
                "authType": constants.BASIC
            }
            audit_data = get_audit_sql_view_data(server, SQL_VIEW_ID)

            save_audit_json(db=db, payload=audit_data)
            save_since()
            print("Audit process completed successfully.")
        except Exception as e:
            print(f"Error during audit process: {e}")
            raise e
