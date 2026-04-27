import json
import os
import logging
from core.common.utils import make_request, generate_headers
from core.common.constants import request_methods
from dotenv import load_dotenv
from core.common.constants import constants, request_methods
import json
import requests

import urllib3
# Desabilita apenas o aviso de certificado não verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


load_dotenv()

os.makedirs("logs", exist_ok=True)


DATA_BASE_DIR = os.getenv("DATA_BASE_DIR", "./data")


def save_erro_log(exception: Exception, index: int, chunk: dict) -> None:
    logging.basicConfig(filename='logs/load_event_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.error(f"Chunk {index} failed: {str(exception)} || Failed data (chunk {index}): {chunk}")
    response_data = None
    if exception.response is not None:
        try:
            response_data = exception.response.json()
        except ValueError:
            response_data = exception.text

    logger.error(f"Error response for (chunk {index}): {response_data}")


def save_succes_log(index: int, response: dict) -> None:
    logging.basicConfig(filename='logs/load_event_success.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.info(f"Response data (chunk {index}): {response}")


def get_audit_sql_view_data(server: dict, view_id: str, since: str, offset_hours: int) -> dict:
    headers = generate_headers(server=server)
    page = 1
    page_size = 100
    all_rows = []
    result = {}

    while True:
        params = f"pageSize={page_size}&page={page}&var=since_datetime:{since}&var=offset_hours:{offset_hours}"
        url = f"{server.get('url')}/api/sqlViews/{view_id}/data.json?{params}"
        response = make_request(url=url, method=request_methods.GET, headers=headers)

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
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 404:
            print(f"Resource not found at URL: {url}")
            return {}
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching resource data: {e}")
        raise e


def get_resources_mapping() -> dict:
    try:
        with open(f"{DATA_BASE_DIR}/klass_resouce_mapping.json", "r") as f:
            mapping = json.load(f)
        return mapping
    except Exception as e:
        print(f"Error loading resource mapping: {e}")
        raise e
