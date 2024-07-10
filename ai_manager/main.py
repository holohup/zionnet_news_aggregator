import asyncio
import logging
import logging.config
from concurrent.futures import ThreadPoolExecutor
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from dapr.clients.exceptions import DaprInternalError
from news_accessor import News_Accessor
from config import load_config


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
news_accessor: News_Accessor = News_Accessor(config.grpc.news_accessor_app_id, config.grpc.db_accessor_app_id)
app = App()


async def news_updater(pause_minutes: int):
    service_up = False
    while not service_up:
        try:
            service_up = await news_accessor.all_accessors_up()
        except DaprInternalError:
            logger.info('News accessor not up yet, waiting 1 more second')
            await asyncio.sleep(1)
    logger.info('News service is up, proceeding')
    try:
        while True:
            await news_accessor.update_news()
            await asyncio.sleep(pause_minutes * 60)
    except Exception as e:
        logger.exception(e)


async def run_app():
    app.run(config.grpc.port)


async def main():
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_app)
        await news_updater(config.news.pause_between_updates_minutes)

if __name__ == '__main__':
    logger.info('Starting AIManager')
    asyncio.run(main())
