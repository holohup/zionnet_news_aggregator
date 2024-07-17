import logging

from config import ServiceConfig
from invokers import publish_message, publish_message_sync
from schema import (CreateDigestAIRequest, GenerateTagsRequest,
                    NewNewsResponse, UserResponse)

logger = logging.getLogger(__name__)


class AI_Accessor:
    """Provides async interface to work with the ai_accessor."""

    def __init__(self, config: ServiceConfig):
        self._config = config

    async def generate_tags(self, id_: int, desc: str, max_tags: int):
        """Publishes a message to ai_accessor to generate the tags."""

        logger.info('Generating tags')
        request = GenerateTagsRequest(id=id_, description=desc, max_tags=max_tags)
        await publish_message(self._config.pubsub, self._config.topic, request.model_dump())
        logger.info(f'Message sent to queue: {request}')

    def create_digest(self, user: UserResponse, news: NewNewsResponse, id_: int):
        """Publishes a request to create digest."""

        logger.info('Placing task to create news digest')
        request = CreateDigestAIRequest(user=user, news=news, id=id_)
        return publish_message_sync(self._config.pubsub, self._config.topic, request.model_dump())
