# gRPC calls to DB Accessor

import json
import logging


from dapr.clients import DaprClient
from dapr.clients.grpc._response import InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

from security import verify_password, create_access_token
from utils import parse_data

logger = logging.getLogger(__name__)


class DB_Accessor:
    """Class incapsulates the methods to work with DB Accessor via gRPC."""

    def __init__(self, app_id) -> None:
        self._app_id = app_id

    def create_user(self, user_data: str) -> str:
        logger.info('Registering user.')
        result = self._invoke_db_method('create_user', user_data)
        logger.info(f'Received response from DB Accessor: {result}')
        return result

    def delete_user(self, email: str) -> str:
        logger.info(f'Deleting user {email}.')
        result = self._invoke_db_method('delete_user', email)
        logger.info(f'Received response from DB Accessor: {result}')
        return result

    def get_user(self, email: str) -> str:
        logger.info(f'Getting user info for {email}')
        result = self._invoke_db_method('get_user_info', email)
        logger.info('Received response from DB Accessor.')
        return result

    def create_token(self, data: str, config) -> str:
        data = parse_data(data)
        email = data['email']
        user_from_db_str = self.get_user(email)
        user_from_db = parse_data(user_from_db_str)
        if user_from_db['status_code'] != 200:
            return user_from_db_str
        if not verify_password(data['password'], user_from_db['detail']['password']):
            return json.dumps({
                'result': 'error', 'status_code': 401, 'detail': 'Incorrect username or password'
            })
        logger.info(f'All checks OK. Generating token for user {email}')
        token = create_access_token(
            {'email': email, 'is_admin': user_from_db['detail']['is_admin']}, config
        )
        logger.info('Token created successfully.')
        return json.dumps({
            'result': 'ok',
            'status_code': 200,
            'detail': {'access_token': token, 'token_type': config.token_type},
        })

    def _invoke_db_method(self, method: str, data) -> str:
        try:
            with DaprClient() as client:
                response: InvokeMethodResponse = client.invoke_method(
                    self._app_id, method, data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return json.dumps(self._server_error_dict)
        return response.text()

    @property
    def _server_error_dict(self):
        return {
            'result': 'error',
            'status_code': 500,
            'detail': 'Internal server error, check UserManager logs',
        }
