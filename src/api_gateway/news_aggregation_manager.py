import logging

from invokers import publish_message
from schema import CreateDigestRequest, User

logger = logging.getLogger(__name__)


class News_Aggregation_Manager:
    def __init__(self, pubsub, topic) -> None:
        self._pubsub = pubsub
        self._topic = topic

    async def create_digest(self, user: User):
        logger.info(f'Received digest creation request from {user.email}')
        request = CreateDigestRequest(email=user.email)
        result = await publish_message(self._pubsub, self._topic, request.model_dump_json())
        return result
