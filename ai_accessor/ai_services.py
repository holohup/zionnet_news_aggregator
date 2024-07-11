import logging

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from config import AIConfig

logger = logging.getLogger(__name__)


class AI:
    def __init__(self, kernel, config) -> None:
        self._kernel = kernel
        self._config: AIConfig = config
        self._plugin = None
        self._init_kernel()

    def _init_kernel(self):
        logger.info(f'Initializing kernel. model = {self._config.model_id}')
        self._kernel.add_service(
            OpenAIChatCompletion(ai_model_id=self._config.model_id, service_id='chat-gpt')
        )
        self._plugin = self._kernel.add_plugin(
            parent_directory='prompt_templates', plugin_name='DigestPlugin'
        )

    async def create_digest(self, input: str, amount_of_sentences: int) -> str:
        return await self._kernel.invoke(self._plugin['digest'], input=input, amount_of_sentences=amount_of_sentences)

    async def generate_tags(self, description: str, maximum_tags: int) -> str:
        return await self._kernel.invoke(self._plugin['tags'], desc=description, amount=maximum_tags)
