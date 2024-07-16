import json
import logging
import logging.config

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse

from config import load_config
from news_updater import NewsUpdater
from schema import NewNewsResponse, News, UpdateNewsRequest
from storage import FileStorage

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
storage = FileStorage(storage_config=config.storage)
updater = NewsUpdater(storage=storage, config=config.parsing)
app: App = App()


@app.subscribe(pubsub_name=config.grpc.pubsub, topic=config.grpc.topic)
def update_news_subscriber(event: v1.Event):
    """Subscribes to the messages and waits for the update_news command to update news."""

    data = json.loads(event.Data())
    logger.info('Received new event')
    if data.get('recipient') != config.service_name:
        logger.info(f'Not for {config.service_name}')
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
    """Returns a PONG when pinged."""

    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')


@app.method('get_new_news')
def get_new_news(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Returns all new news that have appeared after the specified time."""

    from_time = request.text()
    logger.info(f'Preparing new news from {from_time}')
    news = storage.get_all_news_after_strtime(from_time)
    result = NewNewsResponse(
        last_news_time=storage.get_latest_entry_time(),
        news=[News.model_validate(n) for n in news[-config.grpc.max_news_to_return:]]
    )
    logger.info(f'Returning {len(result.news)} entries')
    return result.model_dump_json()


if __name__ == '__main__':
    logger.info(f'Starting {config.service_name}')
    app.run(config.grpc.port)
