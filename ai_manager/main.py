import asyncio
import json
import logging
import logging.config
from dapr.ext.grpc import App
from utils import all_accessors_are_up
from schema import GenerateTagsResponse
from news_accessor import News_Accessor
from ai_accessor import AI_Accessor
from config import load_config
import threading
from cloudevents.sdk.event import v1

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
news_accessor: News_Accessor = News_Accessor(config.grpc)
ai_accessor: AI_Accessor = AI_Accessor(config.grpc.ai)
app = App()


@app.subscribe(config.grpc.ai.pubsub, config.grpc.ai.topic)
def updates_from_ai(event: v1.Event):
    data = json.loads(event.Data())
    logger.info(f'Received event: {data}')
    if not data.get('recipient') == 'ai_manager':
        logger.info('Not for ai_manager')
        return
    if data.get('subject') == 'tags_response':
        response = GenerateTagsResponse.model_validate(data)
        logger.warning(response.id)
        logger.warning(response.result)


async def news_updater(pause_minutes: int):
    logger.info(f'Starting news updater, updates are scheduled every {pause_minutes} minutes')
    while True:
        try:
            await news_accessor.update_news()
            await asyncio.sleep(pause_minutes * 60)
        except Exception as e:
            logger.exception(e)


def run_app():
    app.run(config.grpc.port)


async def main():
    grpc_thread = threading.Thread(target=run_app, daemon=True)
    grpc_thread.start()
    await all_accessors_are_up(seconds=3)
    await news_updater(config.news.pause_between_updates_minutes)


if __name__ == '__main__':
    logger.info('Starting AIManager')
    asyncio.run(main())
