import logging

from schema import UpdateNewsRequest, Tags
from invokers import publish_message, invoke_method

from config import GRPCConfig
logger = logging.getLogger(__name__)


class News_Accessor:
    """Class incapsulates the methods to work with AI Accessor via gRPC."""

    def __init__(self, config: GRPCConfig) -> None:
        self._config = config

    async def update_news(self):
        logger.info('updating news')
        all_tags = await invoke_method(self._config.db_accessor_app_id, 'get_user_tags', '')
        logger.info(f'Tags received: {all_tags}')
        data = UpdateNewsRequest(detail=Tags(tags=all_tags), recipient=self._config.news.app_id)
        await publish_message(self._config.news.pubsub, self._config.news.topic, data.model_dump())
