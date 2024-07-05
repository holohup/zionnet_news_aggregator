import json
from fastapi import HTTPException
import logging


from dapr.aio.clients import DaprClient
from dapr.clients.grpc._response import InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

logging.basicConfig(level=logging.INFO)
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
            raise
        response = json.loads(result.text())
        logger.info(f'Received response from UserManager: {response=}')
        if response['result'] == 'error':
            logger.error(f'Error: {response["detail"]}')
            raise HTTPException(status_code=response['status_code'], detail=response['detail'])
        logger.info('Created successfully.')
        return {s: response[s] for s in ('result', 'status_code', 'detail')}
