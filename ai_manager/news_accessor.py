import logging
import json


from dapr.aio.clients import DaprClient
from dapr.ext.grpc import InvokeMethodRequest, InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError

logger = logging.getLogger(__name__)


class News_Accessor:
    """Class incapsulates the methods to work with AI Accessor via gRPC."""

    def __init__(self, app_id, db_app_id) -> None:
        self._app_id = app_id
        self._db_app_id = db_app_id

    async def update_news(self):
        logger.info('updating news')
        all_tags = await self._invoke_db_method('get_user_tags', '')
        logger.info(f'Tags received: {all_tags}')
        result = await self._invoke_news_method('update_news', json.dumps({'tags': all_tags}))
        if result != 'ok':
            logger.error(result)

    async def all_accessors_up(self) -> bool:
        logger.info('Pinging accessors')
        news_up = await self._invoke_news_method('ping', 'PING') == 'PONG'
        db_up = await self._invoke_db_method('ping', 'PING') == 'PONG'
        return news_up == db_up is True

    async def _invoke_news_method(self, method: str, data) -> str:
        try:
            async with DaprClient() as client:
                response: InvokeMethodResponse = await client.invoke_method(
                    self._app_id, method, data
                )
        except DaprInternalError as e:
            logger.exception(str(e))
            return json.dumps(self._server_error_dict)
        return response.text()

    async def _invoke_db_method(self, method: str, data) -> str:
        try:
            async with DaprClient() as client:
                response: InvokeMethodResponse = await client.invoke_method(
                    self._db_app_id, method, data
                )
        except DaprInternalError as e:
            logger.exception(str(e))
            return json.dumps(self._server_error_dict)
        return response.text()

    @property
    def _server_error_dict(self):
        return {
            'result': 'error',
            'status_code': 500,
            'detail': 'Internal server error, check NewsManager logs',
        }
