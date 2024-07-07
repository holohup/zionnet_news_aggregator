# gRPC calls to DB Accessor

import json
import logging


from dapr.clients import DaprClient
from dapr.clients.grpc._response import InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class DB_Accessor:
    """Class incapsulates the methods to work with DB Accessor via gRPC."""

    def __init__(self, app_id) -> None:
        self._app_id = app_id

    def create_user(self, user_data: str):
        logger.info('Registering user.')
        try:
            with DaprClient() as client:
                response: InvokeMethodResponse = client.invoke_method(
                    self._app_id, 'create_user', user_data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return self._server_error_dict
        result = response.text()
        logger.info(f'Received response from DB Accessor: {result}')
        return result

    def delete_user(self, email: str):
        logger.info(f'Deleting user {email}.')
        try:
            with DaprClient() as client:
                response: InvokeMethodResponse = client.invoke_method(
                    self._app_id, 'delete_user', email
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return self._server_error_dict
        result = response.text()
        logger.info(f'Received response from DB Accessor: {result}')
        return result

    def get_user_info(self, email: str):
        logger.info(f'Getting user info for {email}')
        try:
            with DaprClient() as client:
                response: InvokeMethodResponse = client.invoke_method(
                    self._app_id, 'get_user_info', email
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return self._server_error_dict
        result = response.text()
        logger.info(f'Received response from DB Accessor: {result}')
        return result

    @property
    def _server_error_dict(self):
        return {'result': 'error', 'status_code': 500, 'detail': 'Internal server error, check UserManager logs'}
