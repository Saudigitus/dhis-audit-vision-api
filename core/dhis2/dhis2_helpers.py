import json
import os
import logging
from pathlib import Path
from core.common.utils import make_request, generate_headers
from core.common.constants import request_methods
from dotenv import load_dotenv
from core.common.constants import constants, request_methods
import requests
import re
from datetime import datetime, timezone
from core.common.config import get_dhis2_tls_verify


load_dotenv()

os.makedirs("logs", exist_ok=True)


DATA_BASE_DIR = os.getenv("DATA_BASE_DIR", "./data")
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESOURCE_MAPPING_FILENAMES = (
    "klass_resource_mapping.json",
    "klass_resouce_mapping.json",
)
DEFAULT_RESOURCE_MAPPING = {
    "org.hisp.dhis.category.Category": {"endpoint": "categories"},
    "org.hisp.dhis.category.CategoryCombo": {"endpoint": "categoryCombos"},
    "org.hisp.dhis.category.CategoryOption": {"endpoint": "categoryOptions"},
    "org.hisp.dhis.category.CategoryOptionCombo": {"endpoint": "categoryOptionCombos"},
    "org.hisp.dhis.chart.Chart": {"endpoint": "charts"},
    "org.hisp.dhis.dashboard.Dashboard": {"endpoint": "dashboards"},
    "org.hisp.dhis.dataelement.DataElement": {"endpoint": "dataElements"},
    "org.hisp.dhis.dataelement.DataElementGroup": {"endpoint": "dataElementGroups"},
    "org.hisp.dhis.dataelement.DataElementGroupSet": {"endpoint": "dataElementGroupSets"},
    "org.hisp.dhis.dataset.DataSet": {"endpoint": "dataSets"},
    "org.hisp.dhis.document.Document": {"endpoint": "documents"},
    "org.hisp.dhis.indicator.Indicator": {"endpoint": "indicators"},
    "org.hisp.dhis.indicator.IndicatorGroup": {"endpoint": "indicatorGroups"},
    "org.hisp.dhis.indicator.IndicatorGroupSet": {"endpoint": "indicatorGroupSets"},
    "org.hisp.dhis.legend.LegendSet": {"endpoint": "legendSets"},
    "org.hisp.dhis.option.Option": {"endpoint": "options"},
    "org.hisp.dhis.option.OptionSet": {"endpoint": "optionSets"},
    "org.hisp.dhis.organisationunit.OrganisationUnit": {"endpoint": "organisationUnits"},
    "org.hisp.dhis.organisationunit.OrganisationUnitGroup": {"endpoint": "organisationUnitGroups"},
    "org.hisp.dhis.organisationunit.OrganisationUnitGroupSet": {"endpoint": "organisationUnitGroupSets"},
    "org.hisp.dhis.program.Program": {"endpoint": "programs"},
    "org.hisp.dhis.program.ProgramIndicator": {"endpoint": "programIndicators"},
    "org.hisp.dhis.program.ProgramRule": {"endpoint": "programRules"},
    "org.hisp.dhis.program.ProgramRuleVariable": {"endpoint": "programRuleVariables"},
    "org.hisp.dhis.program.ProgramStage": {"endpoint": "programStages"},
    "org.hisp.dhis.program.ProgramStageDataElement": {"endpoint": "programStageDataElements"},
    "org.hisp.dhis.relationship.RelationshipType": {"endpoint": "relationshipTypes"},
    "org.hisp.dhis.report.Report": {"endpoint": "reports"},
    "org.hisp.dhis.trackedentity.TrackedEntityType": {"endpoint": "trackedEntityTypes"},
    "org.hisp.dhis.user.User": {"endpoint": "users"},
    "org.hisp.dhis.user.UserGroup": {"endpoint": "userGroups"},
    "org.hisp.dhis.validation.ValidationRule": {"endpoint": "validationRules"},
}
DHIS2_UID_PATTERN = re.compile(r"^[A-Za-z0-9]{11}$")
DHIS2_TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}_\d{2}_\d{2}$")


def _validate_offset_hours(offset_hours: int) -> int:
    if isinstance(offset_hours, bool) or not isinstance(offset_hours, int) or not 0 <= offset_hours <= 168:
        raise ValueError("offset_hours must be an integer between 0 and 168")
    return offset_hours


def _timestamp_to_epoch(timestamp: str) -> int:
    _validate_timestamp(timestamp)
    parsed = datetime.strptime(timestamp, "%Y-%m-%d %H_%M_%S").replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


def _validate_timestamp(timestamp: str) -> str:
    if not DHIS2_TIMESTAMP_PATTERN.fullmatch(timestamp):
        raise ValueError("timestamp has an invalid format")
    return timestamp


def _validate_resource_uid(resource_uid: str) -> str:
    if not DHIS2_UID_PATTERN.fullmatch(resource_uid):
        raise ValueError("resource_uid must be an 11-character DHIS2 UID")
    return resource_uid


def _resolve_data_base_dir() -> Path:
    configured_dir = Path(DATA_BASE_DIR)
    if configured_dir.is_absolute():
        return configured_dir
    return PROJECT_ROOT / configured_dir


def _resource_mapping_paths() -> list[Path]:
    data_dir = _resolve_data_base_dir()
    return [data_dir / filename for filename in RESOURCE_MAPPING_FILENAMES]


def save_erro_log(exception: Exception, index: int, chunk: dict) -> None:
    logging.basicConfig(filename='logs/load_event_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.error("Chunk %s failed with %s", index, type(exception).__name__)


def save_succes_log(index: int, response: dict) -> None:
    logging.basicConfig(filename='logs/load_event_success.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("Chunk %s loaded successfully", index)


def get_audit_sql_view_data(server: dict, view_id: str, since: str, offset_hours: int) -> dict:
    headers = generate_headers(server=server)
    page = 1
    page_size = 100
    all_rows = []
    result = {}

    while True:
        params = [
            ("pageSize", page_size),
            ("page", page),
            ("var", f"since_epoch:{_timestamp_to_epoch(since)}"),
            ("var", f"offset_hours:{_validate_offset_hours(offset_hours)}"),
        ]
        url = f"{server.get('url')}/api/sqlViews/{view_id}/data.json"
        response = make_request(url=url, method=request_methods.GET, headers=headers, params=params)

        if not result:
            result = response  # capture full structure on first page

        print(f"Total pages = {response.get('pager', {}).get('pageCount', 1)} - Fetched page {page} with {len(response.get('listGrid', {}).get('rows', []))} rows")

        all_rows.extend(response.get("listGrid", {}).get("rows", []))

        pager = response.get("pager", {})

        if pager.get("page") >= pager.get("pageCount"):
            break

        page += 1

    # update rows and pager with final accumulated data
    result["listGrid"]["rows"] = all_rows
    result["listGrid"]["height"] = len(all_rows)
    result["pager"]["page"] = 1
    result["pager"]["pageSize"] = len(all_rows)

    return result


def get_resouce_object_data(server: dict, resource: str, resource_id: str) -> dict:
    try:
        url = f"{server.get('url')}/api/{resource}/{resource_id}.json?fields=*"
        print(f"Fetching data from URL: {url}")
        headers = generate_headers(server=server)
        response = requests.get(url, headers=headers, verify=get_dhis2_tls_verify())
        if response.status_code == 404:
            print(f"Resource not found at URL: {url}")
            return {}
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching resource data: {e}")
        raise e


def get_resources_mapping() -> dict:
    for mapping_path in _resource_mapping_paths():
        try:
            with mapping_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            continue
        except json.JSONDecodeError as e:
            raise ValueError(f"Resource mapping file is invalid JSON: {mapping_path}") from e

    print(
        "Resource mapping file not found. "
        f"Checked: {', '.join(str(path) for path in _resource_mapping_paths())}. "
        "Using built-in DHIS2 mapping."
    )
    return DEFAULT_RESOURCE_MAPPING


def retrieve_audit_sql_view_data(server: dict, view_id: str, resource_uid: str, created_at: str, offset_hours: int) -> dict:
    headers = generate_headers(server=server)
    params = [
        ("var", f"resource_uid:{_validate_resource_uid(resource_uid)}"),
        ("var", f"created_at:{_validate_timestamp(created_at)}"),
        ("var", f"offset_hours:{_validate_offset_hours(offset_hours)}"),
    ]
    url = f"{server.get('url')}/api/sqlViews/{view_id}/data.json"
    return make_request(url=url, method=request_methods.GET, headers=headers, params=params)


def extract_all_ids(data: dict | list, seen: set = None) -> list[str]:
    """
    Recursively extracts all 'id' values from a nested dict/list structure.
    Uses a set to avoid duplicates.
    """
    if seen is None:
        seen = set()

    if isinstance(data, dict):
        if "id" in data and data["id"] not in seen:
            seen.add(data["id"])
        for value in data.values():
            extract_all_ids(value, seen)

    elif isinstance(data, list):
        for item in data:
            extract_all_ids(item, seen)

    return list(seen)


def get_dhis2_program(server: dict, program_id: str) -> dict:
    headers = generate_headers(server=server)
    url = f"{server.get('url')}/api/programs/{program_id}.json?fields=*"
    return make_request(url=url, method=request_methods.GET, headers=headers)


def get_dhis2_dataset(server: dict, dataset_id: str) -> dict:
    headers = generate_headers(server=server)
    url = f"{server.get('url')}/api/dataSets/{dataset_id}.json?fields=*"
    return make_request(url=url, method=request_methods.GET, headers=headers)


def get_program_dependants(server: dict, program_id: str) -> dict:
    try:
        program = get_dhis2_program(server, program_id)
        all_ids = extract_all_ids(program)
        return all_ids
    except Exception as e:
        print(f"Error fetching program dependants: {e}")
        raise e


def get_dataset_dependants(server: dict, dataset_id: str) -> dict:
    try:
        dataset = get_dhis2_dataset(server, dataset_id)
        all_ids = extract_all_ids(dataset)
        return all_ids
    except Exception as e:
        print(f"Error fetching dataset dependants: {e}")
        raise e
