import logging

from config import GRPCConfig
from dapr.clients import DaprClient, DaprInternalError
from schema import GenerateTagsRequest

logger = logging.getLogger(__name__)


class AI_Accessor:
    def __init__(self, max_tags: int, config: GRPCConfig) -> None:
        self._max_tags = max_tags
        self._config = config
        self._max_tags = max_tags

    def queue_tags_generation(self, id_: int, info: str):
        request = GenerateTagsRequest(recipient='ai_accessor', id=id_, description=info, max_tags=self._max_tags)
        self._send_request_to_queue(request)

    def _send_request_to_queue(self, request):
        logger.info('Trying to publish a message')
        try:
            with DaprClient() as client:
                client.publish_event(self._config.pubsub, self._config.topic, request.model_dump_json())
        except DaprInternalError:
            logger.exception('Could not publish message')
        else:
            logger.info('Message published successfully')
