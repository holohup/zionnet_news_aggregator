import json
from fastapi import HTTPException
import logging


from dapr.aio.clients import DaprClient
from dapr.clients.grpc._response import InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class UserManager:
    """Class incapsulates the methods to work with UserManager via gRPC."""

    def __init__(self, app_id) -> None:
        self._app_id = app_id

    async def register_user(self, user_data: str):
        logger.info('Registering user.')
        try:
            async with DaprClient() as client:
                result: InvokeMethodResponse = await client.invoke_method(
                    self._app_id, 'register_user', user_data
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return self._server_error_dict
        response = json.loads(result.text())
        logger.info(f'Received response from UserManager: {response=}')
        if response['result'] == 'error':
            logger.error(f'Error: {response["detail"]}')
            raise HTTPException(status_code=response['status_code'], detail=response['detail'])
        logger.info('Created successfully.')
        return self._response_to_dict(response)

    async def delete_user(self, email: str):
        logger.info(f'Deleting user {email}.')
        try:
            async with DaprClient() as client:
                result: InvokeMethodResponse = await client.invoke_method(
                    self._app_id, 'delete_user', email
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return self._server_error_dict
        response = json.loads(result.text())
        logger.info(f'Received response from UserManager: {response=}')
        if response['result'] == 'error':
            logger.error(f'Error: {response["detail"]}')
            raise HTTPException(status_code=response['status_code'], detail=response['detail'])
        logger.info('Deleted successfully.')

    async def get_user(self, email: str):
        logger.info(f'Getting user info for {email}.')
        try:
            async with DaprClient() as client:
                result: InvokeMethodResponse = await client.invoke_method(
                    self._app_id, 'get_user', email
                )
        except DaprInternalError as e:
            logger.error(str(e))
            return self._server_error_dict
        response = json.loads(result.text())
        logger.info(f'Received response from UserManager: {response=}')
        if response['result'] == 'error':
            logger.error(f'Error: {response["detail"]}')
            raise HTTPException(status_code=response['status_code'], detail=response['detail'])
        logger.info(f'Fetched successfully: {response}.')
        return self._response_to_dict(response)

    def _response_to_dict(self, response):
        return {s: response[s] for s in ('result', 'status_code', 'detail')}

    @property
    def _server_error_dict(self):
        return {'result': 'error', 'status_code': 500, 'detail': 'Internal server error, check API Gateway logs'}
