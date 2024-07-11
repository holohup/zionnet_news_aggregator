import logging
import json


from dapr.aio.clients import DaprClient
from dapr.ext.grpc import InvokeMethodRequest, InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError
from schema import UpdateNewsRequest, GenerateTagsRequest, Tags
from config import GRPCConfig

logger = logging.getLogger(__name__)


class News_Accessor:
    """Class incapsulates the methods to work with AI Accessor via gRPC."""

    def __init__(self, config: GRPCConfig) -> None:
        self._app_id = config.news.app_id
        self._db_app_id = config.db_accessor_app_id
        self._config = config

    async def update_news(self):
        logger.info('updating news')
        all_tags = await self._invoke_db_method('get_user_tags', '')
        logger.info(f'Tags received: {all_tags}')
        data = UpdateNewsRequest(detail=Tags(tags=all_tags))
        await self._publish_message(self._config.news.pubsub, self._config.news.topic, data.model_dump())

    async def all_accessors_up(self) -> bool:
        logger.info('Pinging accessors')
        try:
            news_up = await self._invoke_news_method('ping', 'PING') == 'PONG'
            db_up = await self._invoke_db_method('ping', 'PING') == 'PONG'
            ai_up = await self._invoke_ai_method('ping', 'PING') == 'PONG'
        except DaprInternalError:
            return False
        return True

    async def generate_tags(self, id_: int, desc: str, max_tags: int):
        logger.info('Generating tags')
        request = GenerateTagsRequest(id=id_, description=desc, max_tags=max_tags)
        await self._publish_message(self._config.ai.pubsub, self._config.ai.topic, request.model_dump())
        logger.info(f'Message sent to queue: {request}')

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

    async def _invoke_ai_method(self, method: str, data) -> str:
        try:
            async with DaprClient() as client:
                response: InvokeMethodResponse = await client.invoke_method(
                    self._config.ai.app_id, method, data
                )
        except DaprInternalError as e:
            logger.exception(str(e))
            return json.dumps(self._server_error_dict)
        return response.text()

    async def _publish_message(self, pubsub_name: str, topic_name: str, data: dict):
        try:
            async with DaprClient() as client:
                await client.publish_event(pubsub_name=pubsub_name, topic_name=topic_name, data=json.dumps(data))
        except DaprInternalError as e:
            logger.exception(e)

    @property
    def _server_error_dict(self):
        return {
            'result': 'error',
            'status_code': 500,
            'detail': 'Internal server error, check NewsManager logs',
        }
