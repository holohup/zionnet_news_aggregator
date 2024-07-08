import json
from typing import Annotated
import logging

from fastapi import Depends
import jwt

from exceptions import server_error_dict, credentials_exception, http_exception
from schema import Token

from dapr.aio.clients import DaprClient
from dapr.clients.grpc._response import InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class UserManager:
    """Class incapsulates the methods to work with UserManager via gRPC."""

    def __init__(self, app_id: str, token_config) -> None:
        self._app_id = app_id
        self._token_config = token_config

    async def register_user(self, user_data: str) -> dict:
        logger.info('Registering user.')
        result = await self._invoke_user_manager_method('register_user', user_data)
        logger.info(f'Created successfully. {result=}')
        return result

    async def delete_user(self, email: str) -> dict:
        logger.info(f'Deleting user {email}.')
        await self._invoke_user_manager_method('delete_user', email)
        logger.info('Deleted successfully.')

    async def get_user(self, email: str) -> dict:
        logger.info(f'Getting user info for {email}.')
        result = await self._invoke_user_manager_method('get_user', email)
        logger.info('Fetched successfully.')
        return result

    async def create_token(self, email, password) -> dict:
        logger.info(f'Creating token for {email}')
        result = await self._invoke_user_manager_method(
            'create_token', json.dumps({'email': email, 'password': password})
        )
        logger.info('Received token.')
        token = result['detail']
        return token

    async def get_current_user(self, token: Annotated[str, Depends(Token)]):

        logger.info('Getting credentials')
        try:
            payload = jwt.decode(
                token.access_token,
                self._token_config.secret_key,
                algorithms=[self._token_config.algorithm],
            )
            logger.info(f'Received payload: {payload}')
            email: str = payload.get('email')
        except jwt.InvalidTokenError:
            raise credentials_exception
        response = await self.get_user(email=email)
        user = response['detail']
        return {'email': email, 'is_admin': user['is_admin']}

    async def _invoke_user_manager_method(self, method: str, data) -> dict:
        try:
            async with DaprClient() as client:
                response: InvokeMethodResponse = await client.invoke_method(
                    self._app_id, method, data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return server_error_dict
        result = json.loads(response.text())
        if result['result'] == 'error':
            logger.error(f'Error: {result["detail"]}')
            raise http_exception(result)
        return result
