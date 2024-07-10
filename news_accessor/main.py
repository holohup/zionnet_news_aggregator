from datetime import datetime
import json
import logging
import logging.config

from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse

from config import load_config
from schema import ParseSettings
from storage import FileStorage
from news_updater import NewsUpdater

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
storage = FileStorage(config.filenames)
updater = NewsUpdater(storage, config.parsing)
app: App = App()


@app.method('update_news')
def update_news(request: InvokeMethodRequest) -> InvokeMethodResponse:
    logger.info(f'Received news update request: {request.text()}')
    if not request.text():
        logger.warning('Empty tag list provided, returning')
        return InvokeMethodResponse(data='ok')
    try:
        updater.update_news(request.text())
    except Exception as e:
        logger.exception(f'Failed to update news: {str(e)}')
        return InvokeMethodResponse(data=str(e))
    else:
        logger.info('Parse complete')
    return InvokeMethodResponse(data='ok')


@app.method('ping')
def ping_service(request: InvokeMethodRequest) -> InvokeMethodResponse:
    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')

class Fake:
    def __init__(self) -> None:
        pass

    def text(self):
        return json.dumps(
            {'tags': 'Biden, tesla, us, celebrities', 'source_countries': 'us, il'}
        )


if __name__ == '__main__':
    logger.info('Starting db_accessor')
    app.run(config.grpc.port)


# update_news(Fake())
# storage.delete_old_entries(config.parsing.news_expiration_hours)
# print(storage.get_latest_entry_time())
# a = storage.get_all_news_after_datetime(datetime.strptime('2024-07-09 18:06:30', '%Y-%m-%d %H:%M:%S'))
