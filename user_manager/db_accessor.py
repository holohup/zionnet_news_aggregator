# gRPC calls to DB Accessor

import json
import logging

from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError
from dapr.clients.grpc._response import InvokeMethodResponse
from id_accountant import IDAccountant
from responses import (credentials_error, hash_error, server_error,
                       token_response)
from schema import RegistrationRequest, UserRegistrationSettings, UserWithEmail
from security import create_access_token, verify_password

from ai_accessor import AI_Accessor

logger = logging.getLogger(__name__)


class DB_Accessor:
    """Class incapsulates the methods to work with DB Accessor via gRPC."""

    def __init__(self, app_id, accountant: IDAccountant, ai_accessor: AI_Accessor) -> None:
        self._app_id = app_id
        self._emails = accountant
        self._ai = ai_accessor

    def create_user(self, user_request: RegistrationRequest) -> str:
        user = UserWithEmail(
            email=user_request.email,
            password=user_request.password,
            contact_info=user_request.contact_info,
            settings=UserRegistrationSettings(info=user_request.info)
        )
        logger.info('Registering user.')
        result = self._invoke_db_method('create_user', user.model_dump_json())
        logger.info(f'Received response from DB Accessor: {result}')
        if json.loads(result)['result'] != 'error':
            logger.info('Generating tags for the new user')
            id_ = self._emails.new_id(user_request.email.lower())
            self._ai.queue_tags_generation(id_, user.settings.info)
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

    def update_settings(self, data: str) -> str:
        logger.info('Updating settings.')
        result = self._invoke_db_method('update_user_settings', data)
        logger.info('Received response from DB Accessor.')
        return result

    def create_token(self, req_data: str, config) -> str:
        data = json.loads(req_data)
        email = data['email']
        hash_response = json.loads(self._invoke_db_method('get_password_hash', email))
        if hash_response['status_code'] != 200:
            return hash_error
        if not verify_password(data['password'], hash_response['detail']):
            return credentials_error
        logger.info(f'All checks OK. Generating token for user {email}')
        user_from_db = json.loads(self.get_user(email))
        token = create_access_token(
            {'email': email, 'is_admin': user_from_db['detail']['is_admin']}, config
        )
        logger.info('Token created successfully.')
        return token_response(token, config.token_type)

    def _invoke_db_method(self, method: str, data) -> str:
        try:
            with DaprClient() as client:
                response: InvokeMethodResponse = client.invoke_method(
                    self._app_id, method, data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return server_error
        return response.text()
