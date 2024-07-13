import json
import logging
from datetime import datetime

import jwt

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from invokers import invoke_grpc_method
from pydantic import ValidationError
from schema import (RegistrationRequest, TokenPayload,
                    UpdateUserSettingsRequest, User)

from exceptions import credentials_exception, token_expired_exception


logger = logging.getLogger(__name__)

reuseable_oauth = OAuth2PasswordBearer(tokenUrl='/login', scheme_name='JWT')


class UserManager:
    """Class incapsulates the methods to work with UserManager via gRPC."""

    def __init__(self, app_id: str, token_config) -> None:
        self._app_id = app_id
        self._token_config = token_config

    async def register_user(self, user_data: RegistrationRequest) -> dict:
        logger.info('Registering user.')
        result = await invoke_grpc_method(
            self._app_id, 'register_user', user_data.model_dump_json()
        )
        logger.info(f'Created successfully. {result=}')
        return result

    async def delete_user(self, email: str) -> dict:
        logger.info(f'Deleting user {email}.')
        await invoke_grpc_method(self._app_id, 'delete_user', email)
        logger.info('Deleted successfully.')

    async def get_user(self, email: str) -> dict:
        logger.info(f'Getting user info for {email}.')
        result = await invoke_grpc_method(self._app_id, 'get_user', email)
        logger.info('Fetched successfully.')
        return result

    async def update_settings(self, request: UpdateUserSettingsRequest) -> dict:
        result = await invoke_grpc_method(
            self._app_id, 'update_settings', request.model_dump_json()
        )
        logger.info('Received response from UserManager')
        return result

    async def create_token(self, email, password) -> dict:
        logger.info(f'Creating token for {email}')
        result = await invoke_grpc_method(
            self._app_id,
            'create_token',
            json.dumps({'email': email, 'password': password}),
        )
        logger.info('Received token.')
        token = result['detail']
        return token

    async def get_current_user(self, access_token: str = Depends(reuseable_oauth)):
        logger.info('Getting credentials')
        try:
            payload = jwt.decode(
                access_token,
                self._token_config.secret_key,
                algorithms=[self._token_config.algorithm],
            )
            logger.info(f'Received payload: {payload}')
            token_data = TokenPayload(**payload)
        except (ValidationError, jwt.PyJWTError):
            logger.info('Token not valid')
            raise credentials_exception
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            logger.info(f'Token expired. {token_data.exp}, {type(token_data.exp)}')
            raise token_expired_exception
        response = await self.get_user(email=token_data.email)
        user = response['detail']
        user.update({'email': token_data.email})
        return User(**user)
