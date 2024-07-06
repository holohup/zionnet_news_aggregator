# gRPC calls to DB Accessor

import json
import logging


from dapr.clients import DaprClient
from dapr.clients.grpc._response import InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DB_Accessor:
    """Class incapsulates the methods to work with DB Accessor via gRPC."""

    def __init__(self, app_id) -> None:
        self._app_id = app_id

    def create_user(self, user_data: str):
        logger.info('Registering user.')
        try:
            with DaprClient() as client:
                result: InvokeMethodResponse = client.invoke_method(
                    self._app_id, 'create_user', user_data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            raise
        response = json.loads(result.text())
        logger.info(f'Received response from DB Accessor: {response=}')
        return self._response_to_dict(response)

    def delete_user(self, user_data: str):
        logger.info('Deleting user.')
        try:
            with DaprClient() as client:
                result: InvokeMethodResponse = client.invoke_method(
                    self._app_id, 'delete_user', user_data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            raise
        response = json.loads(result.text())
        logger.info(f'Received response from DB Accessor: {response=}')
        return self._response_to_dict(response)

    def _response_to_dict(self, response):
        return {s: response[s] for s in ('result', 'status_code', 'detail')}
