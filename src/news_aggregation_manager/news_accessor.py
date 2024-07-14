import json
import logging

from config import GRPCConfig
from invokers import invoke_method, invoke_method_sync, publish_message
from schema import NewNewsResponse, Tags, UpdateNewsRequest

logger = logging.getLogger(__name__)


class News_Accessor:
    """Class incapsulates the methods to work with News Accessor via gRPC."""

    def __init__(self, config: GRPCConfig) -> None:
        self._config = config

    async def update_news(self) -> None:
        """Issues a command to update news."""

        logger.info('updating news')
        all_tags = await invoke_method(self._config.db_accessor_app_id, 'get_user_tags', '')
        if not all_tags:
            logger.info('No tags for users in system yet. Not proceeding.')
            return
        logger.info(f'Tags received: {all_tags}')
        data = UpdateNewsRequest(detail=Tags(tags=all_tags), recipient=self._config.news.app_id)
        await publish_message(self._config.news.pubsub, self._config.news.topic, data.model_dump())

    def get_new_news(self, update_from: str) -> list:
        """Fetches new news after specific time."""

        logger.info('Getting new news')
        news = NewNewsResponse.model_validate(
            json.loads(invoke_method_sync(self._config.news.app_id, 'get_new_news', update_from))
        )
        logger.info(f'Fetched {len(news.news)} news.')
        return news
