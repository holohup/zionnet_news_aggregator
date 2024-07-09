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
updater = NewsUpdater(storage, config.api_key)


def parse_request(request: str) -> dict:
    req_json = json.loads(request)
    parse_config = ParseSettings(
        text=' OR '.join([tag.strip() for tag in req_json['tags'].split(',')]),
        number=config.parsing.max_entries
    )
    return parse_config


def update_news(request: InvokeMethodRequest) -> InvokeMethodResponse:
    logger.info(f'Received news update request: {request.text()}')
    config = parse_request(request.text())
    logger.info(f'Trying to update news with {config=}')
    try:
        updater.update_news(config.dict)
    except Exception as e:
        logger.error(f'Failed to update news: {str(e)}')
        raise
    else:
        logger.info('Parse success')


class Fake:
    def __init__(self) -> None:
        pass

    def text(self):
        return json.dumps({'tags': 'putin, tesla, us, celebrity, madonna, ice cube'})

update_news(Fake())
# delete_old_entries(datetime.strptime('2024-07-08 13:00:00', '%Y-%m-%d %H:%M:%S'))