from core.common.constants import constants, request_methods
import json
import requests
import isodate
from core.common.config import get_dhis2_tls_verify


def make_hash(list: list, key: str) -> dict:
    return {item[key]: item for item in list}


def make_request(url: str, method: str = request_methods.GET, headers: dict = None, payload: dict = None, params=None) -> dict:
    try:
        verify = get_dhis2_tls_verify()

        if method == request_methods.POST:
            response = requests.post(url, headers=headers, data=json.dumps(payload), params=params, verify=verify)
            _raise_for_status_with_body(response)
            return response.json()

        if method == request_methods.GET:
            response = requests.get(url, headers=headers, params=params, verify=verify)
            _raise_for_status_with_body(response)
            return response.json()

        if method == request_methods.PUT:
            response = requests.put(url, headers=headers, data=json.dumps(payload), params=params, verify=verify)
            _raise_for_status_with_body(response)
            return response.json()

        return None

    except Exception as e:
        print(f"Error during request: {e}")
        raise e


def _raise_for_status_with_body(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as exc:
        body = response.text[:1000] if response.text else "<empty response body>"
        raise requests.exceptions.HTTPError(
            f"{exc} - response body: {body}",
            response=response,
        ) from exc


def generate_headers(server: dict) -> dict:

    if server.get('authType', {}) == constants.BASIC:
        return {"Authorization": f"Basic {server.get('auth')}", 'Accept': 'application/json',
                'Content-Type': 'application/json'}
    return None


def get_value_from_path(data: dict, path: str):

    keys = path.split('.')  # Split the path into keys based on dot notation.

    keys = [str(key).replace("_DOT_", ".") for key in keys]

    checked_indexes = []

    # Traverse through the nested structure using the keys.
    for index, key in enumerate(keys):

        if index not in checked_indexes:

            checked_indexes.append(index)

            if isinstance(data, list):  # If the current data is a list, look for an object with a matching 'attribute'.

                if (index + 1) < len(keys):
                    next_index = index + 1
                    checked_indexes.append(next_index)

                    found = False
                    for item in data:
                        if item[key] == keys[next_index]:
                            data = item
                            found = True
                            break

                    if found is False:
                        return None

                else:
                    return data

            else:
                data = data.get(key, None)  # Access the key directly from the dictionary.

            if data is None:
                return None  # Return None if any key/path is not found.

    value = None
    if type(data) is bool or data is None:
        value = data
    else:
        value = str(data).replace("mailto:", "")
    return value  # Return the final accessed value.


def valueHandler(value, mapping):
    handler = mapping.get('valueHandler')

    if handler == constants.LOWER:
        return str(value).lower()
    elif handler == constants.SPLIT_LOWER:
        return str(value).split('/')[-1].lower()
    return value


def valueHandlerDuration(value, mapping):
    handler = mapping.get('valueHandlerDuration')

    if handler == constants.DURATION:
        duration = isodate.parse_duration(value)
        seconds = int(duration.total_seconds())
        return seconds

    return value


def get_value_from_mapping(value: str, mapping: dict):

    if 'defaultValue' in mapping and value is None:
        return mapping['defaultValue']

    value = valueHandlerDuration(value, mapping)

    if "options" in mapping:
        for option in mapping['options']:
            if value == option['originValue']:
                return valueHandler(value, mapping)

    # if 'type' in mapping:
    #     mapping['type'] == "DATE"
    #     date = get_date_with_format(date=value)
    #     return date

    return valueHandler(value, mapping)


def get_value(data: dict, path: str, mapping: dict):

    if 'originId' not in mapping or mapping['originId'] == "" or mapping['originId'] is None:
        if 'defaultValue' in mapping:
            return mapping['defaultValue']
        else:
            raise ValueError("A mapping without origin ID should have a default value")

    value = get_value_from_path(data=data, path=path)
    return get_value_from_mapping(value=value, mapping=mapping)
