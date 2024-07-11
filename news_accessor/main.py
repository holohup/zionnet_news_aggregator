import json
import logging
import logging.config
from cloudevents.sdk.event import v1
from dapr.ext.grpc import App, InvokeMethodResponse, InvokeMethodRequest

from config import load_config
from storage import FileStorage
from schema import UpdateNewsRequest
from news_updater import NewsUpdater

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
storage = FileStorage(config.filenames)
updater = NewsUpdater(storage, config.parsing)
app: App = App()


@app.subscribe(pubsub_name=config.grpc.pubsub, topic=config.grpc.topic)
def update_news(event: v1.Event):
    data = json.loads(event.Data())
    logger.info(f'Received news update request: {data}')
    if data.get('recipient') != 'news_accessor':
        logger.info('Not for news_accessor')
        return
    if data.get('subject') == 'update_news':
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


if __name__ == '__main__':
    logger.info('Starting News Accessor')
    app.run(config.grpc.port)
