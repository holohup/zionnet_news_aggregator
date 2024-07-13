import json
import logging
import logging.config

from cloudevents.sdk.event import v1
from config import load_config
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from news_updater import NewsUpdater
from schema import NewNewsResponse, News, UpdateNewsRequest
from storage import FileStorage

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
storage = FileStorage(config.filenames)
updater = NewsUpdater(storage, config.parsing)
app: App = App()


@app.subscribe(pubsub_name=config.grpc.pubsub, topic=config.grpc.topic)
def update_news(event: v1.Event):
    data = json.loads(event.Data())
    logger.info('Received new event')
    if data.get('recipient') != 'news_accessor':
        logger.info('Not for news_accessor')
        return

    if data.get('subject') == 'update_news':
        logger.info(f'Received news update request {data}')
        request = UpdateNewsRequest.model_validate(data)
        try:
            updater.update_news(request.detail)
        except Exception as e:
            logger.exception(f'Failed to update news: {str(e)}')
        else:
            logger.info('Parse complete')


@app.method('ping')
def ping_service(request: InvokeMethodRequest) -> InvokeMethodResponse:
    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')


@app.method('get_new_news')
def get_new_news(request: InvokeMethodRequest) -> InvokeMethodResponse:
    from_time = request.text()
    logger.info(f'Preparing new news from {from_time}')
    news = storage.get_all_news_after_strtime(from_time)
    result = NewNewsResponse(
        last_news_time=storage.get_latest_entry_time(),
        news=[News.model_validate(n) for n in news]
    )
    logger.info(f'Returning {len(result.news)} entries')
    return result.model_dump_json()


if __name__ == '__main__':
    logger.info('Starting News Accessor')
    app.run(config.grpc.port)
