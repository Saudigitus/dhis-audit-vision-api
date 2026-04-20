import os
import logging
from core.models.models import Server
from core.common.utils import make_request, generate_headers, get_global_configurations, get_value_from_path
from core.common.constants import request_methods
from core.common.utils import make_request


os.makedirs("logs", exist_ok=True)


def get_program(program_id: str, server: Server) -> dict:
    url = f"{server.url}/api/programs/{program_id}.json?fields=id,name,trackedEntityType,programTrackedEntityAttributes[trackedEntityAttribute[id,name]],programStages[id,name,repeatable,programStageDataElements[dataElement[id,name]]]"
    headers = generate_headers(server=server)
    response = make_request(url=url, method=request_methods.GET, headers=headers)
    return response


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
