import asyncio
import json
import logging
import logging.config
import threading

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from pydantic import ValidationError

from ai_accessor import AI_Accessor
from config import load_config
from db_accessor import DB_Accessor
from id_accountant import IDAccountant
from news_accessor import News_Accessor
from processors import MessageProcessor
from routes import parse_details
from utils import all_accessors_are_up


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
accountant = IDAccountant()
news_accessor: News_Accessor = News_Accessor(config=config.grpc)
ai_accessor: AI_Accessor = AI_Accessor(config=config.grpc.ai)
db_accessor: DB_Accessor = DB_Accessor(db_app_id=config.grpc.db_accessor_app_id)
processor: MessageProcessor = MessageProcessor(
    ai=ai_accessor, db=db_accessor, news=news_accessor, id_acc=accountant, report_config=config.grpc.tg
)

app = App()


@app.subscribe(config.grpc.ai.pubsub, config.grpc.ai.topic)
def consumer(event: v1.Event) -> None:
    """Messages consumer."""

    data = json.loads(event.Data())
    logger.info('Received event.')
    if data.get('subject') not in parse_details.keys():
        logger.info(f'Not for {config.service_name}')
        return
    try:
        message_processor = parse_details[data['subject']]
        validated_data = message_processor.model(**data)
        getattr(processor, message_processor.processor)(validated_data)
    except KeyError:
        logger.error(f'Unknown subject: {data["subject"]}')
    except ValidationError as e:
        logger.error(f'Validation error: {e}')
    except Exception as e:
        logger.error(f'Error processing message: {e}')


@app.method('ping')
def ping_service(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Returns pong when pinged."""

    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')


async def news_updater(pause_minutes: int) -> None:
    """Issues a news update request message on startup and then every pause_minutes minutes."""

    logger.info(f'Starting news updater, updates are scheduled every {pause_minutes} minutes')
    while True:
        logger.info('Issuing an order to update news!')
        try:
            await news_accessor.update_news()
            await asyncio.sleep(pause_minutes * 60)
        except Exception as e:
            logger.exception(e)


def run_app():
    """Runs DAPR."""

    app.run(config.grpc.port)


async def main() -> None:
    """Star up routine.
    Creates a separate thread for DAPR. Waits for all accessors to start,
    then starts the new updater service."""

    grpc_thread = threading.Thread(target=run_app, daemon=True)
    grpc_thread.start()
    await all_accessors_are_up(seconds=3)
    await news_updater(config.news.pause_between_updates_minutes)


if __name__ == '__main__':
    logger.info(f'Starting {config.service_name}')
    asyncio.run(main())
