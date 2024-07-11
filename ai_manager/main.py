import asyncio
import json
import logging
import logging.config
from concurrent.futures import ThreadPoolExecutor
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError
from schema import GenerateTagsResponse
from news_accessor import News_Accessor
from config import load_config
import threading
from cloudevents.sdk.event import v1

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
news_accessor: News_Accessor = News_Accessor(config.grpc)
app = App()


@app.subscribe(config.grpc.ai.pubsub, config.grpc.ai.topic)
def updates_from_ai(event: v1.Event):
    data = json.loads(event.Data())
    logger.info(f'Received event: {data}')
    if data.get('subject') == 'tags_response':
        response = GenerateTagsResponse.model_validate(data)
        logger.warning(response.id)
        logger.warning(response.result)


async def news_updater(pause_minutes: int):
    service_up = False
    while not service_up:
        service_up = await news_accessor.all_accessors_up()
        await asyncio.sleep(5)
    logger.info('All services up, proceeding')
    await news_accessor.generate_tags(111, 'I am a junior programmer, I live in DC, I am interested in football and celebrities', 5)
    try:
        while True:
            await news_accessor.update_news()
            await asyncio.sleep(pause_minutes * 60)
    except Exception as e:
        logger.exception(e)


def run_app():
    app.run(config.grpc.port)


async def main():
    grpc_thread = threading.Thread(target=run_app, daemon=True)
    grpc_thread.start()
    await news_updater(config.news.pause_between_updates_minutes)


if __name__ == '__main__':
    logger.info('Starting AIManager')
    asyncio.run(main())
