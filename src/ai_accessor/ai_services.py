import logging
from typing import NamedTuple
from xml.sax.saxutils import escape

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from config import AIConfig
from schema import CreateDigestAIRequest, DigestEntry

logger = logging.getLogger(__name__)


class NewsEntry(NamedTuple):
    """A simple DTO for news entries."""

    url: str
    text: str
    summary: str
    title: str


class AI:
    """Class to communicate with the  OpenAI API.
    Provides generate_tags and generate_digest methods."""

    def __init__(self, kernel, config) -> None:
        self._kernel = kernel
        self._config: AIConfig = config
        self._plugin = None
        self._init_kernel()

    def _init_kernel(self):
        """OpenAI kernel initialization."""

        logger.info(f'Initializing kernel. model = {self._config.model_id}')
        self._kernel.add_service(
            OpenAIChatCompletion(ai_model_id=self._config.model_id, service_id='chat-gpt')
        )
        self._plugin = self._kernel.add_plugin(
            parent_directory='prompt_templates', plugin_name='DigestPlugin'
        )

    async def generate_tags(self, description: str, maximum_tags: int) -> str:
        """Generates a list of comma-separated tags from user description."""

        return await self._kernel.invoke(self._plugin['tags'], desc=description, amount=maximum_tags)

    async def generate_digest(self, request: CreateDigestAIRequest) -> list[dict]:
        """Generates a digest from user description and tags."""

        logger.info('Starting digest generation.')
        if not request.news.news:
            logger.info('No news for today')
            return []
        news_by_id = {
            n.id: NewsEntry(
                url=n.url, text=n.text, summary=n.summary, title=n.title
            ) for n in request.news.news
        }
        interesting_ids = await self._get_most_interesting_ids(request)
        if not interesting_ids:
            logger.info('No interesting news for today')
            return []
        result = [DigestEntry(
            url=news_by_id[id_].url,
            text=str(await self._create_digest(news_by_id[id_].text, request.user.settings.max_sentences))
        ) for id_ in interesting_ids]
        logger.info('Received digest generation result, proceeding')
        return result

    async def _get_most_interesting_ids(self, request: CreateDigestAIRequest) -> list[int]:
        """Polls the AI to find the ids of most interesting news.
        Uses user info, tags and news titles and summaries."""

        user_description = request.user.settings.info
        user_tags = request.user.settings.tags
        news = [{'id': n.id, 'summary': escape(n.title + '\n' + '' or n.summary)} for n in request.news.news if n.id and n.title]
        logger.info('All variables ready, requesting AI help')
        result = await self._kernel.invoke(
            self._plugin['pick_news'],
            news=news,
            tags=user_tags,
            desc=user_description,
            max_news=request.user.settings.max_news
        )
        logger.info(f'Most interestings IDs received: {result}')
        return [int(n.strip()) for n in str(result).split(',')]

    async def _create_digest(self, input: str, amount_of_sentences: int) -> str:
        """Creates a digest from news text and max amount of sentences."""

        return await self._kernel.invoke(
            self._plugin['digest'], input=input, amount_of_sentences=amount_of_sentences
        )
