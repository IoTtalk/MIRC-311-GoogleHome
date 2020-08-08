import json

from pathlib import Path


def get_device_data(device_json_file_path: str) -> list:
    """Parse the device json file and return its content as a list of devices

    :param device_json_file_path: Device json file path
    :type device_json_file_path: str
    :return: List of devices
    :rtype: list
    """
    if not device_json_file_path or not Path(device_json_file_path).exists():
        raise OSError('Device json file does not exist')

    with open(device_json_file_path) as f:
        file_content = f.read()

    try:
        device_data = json.loads(file_content)
    except json.JSONDecodeError:
        device_data = []

    return device_data


def handle_execute_intent(commands: list) -> list:
    """Handle EXECUTE intent

    :param commands: List of commands
    :type commands: list
    :return: List of execution results
    :rtype: list
    """
    return [
        {
            'ids': [device['id'] for command in commands for device in command['devices']],
            'status': 'SUCCESS'
        }
    ]


def hanlde_query_intent(devices: list) -> dict:
    """Currently, this intent is not available.

    Use ``actionNotAvailable`` ERROR to response

    :param devices: List of devices
    :type devices: list
    :return: List of query results
    :rtype: list
    """
    response_dict = {}

    for device in devices:
        device_id = device.get('id')

        if device_id:
            response_dict[device_id] = \
                {'errorCode': 'actionNotAvailable', 'status': 'ERROR'}

    return response_dict
