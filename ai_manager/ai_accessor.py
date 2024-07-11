import logging

from schema import GenerateTagsRequest
from invokers import publish_message
from config import ServiceConfig

logger = logging.getLogger(__name__)


class AI_Accessor:
    def __init__(self, config: ServiceConfig):
        self._config = config

    async def generate_tags(self, id_: int, desc: str, max_tags: int):
        logger.info('Generating tags')
        request = GenerateTagsRequest(id=id_, description=desc, max_tags=max_tags, recipient='ai_accessor')
        await publish_message(self._config.pubsub, self._config.topic, request.model_dump())
        logger.info(f'Message sent to queue: {request}')
