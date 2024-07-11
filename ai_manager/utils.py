import asyncio
import logging
from dapr.aio.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError
logger = logging.getLogger(__name__)


async def all_accessors_are_up(seconds):
    services_not_up = ['ai_accessor', 'news_accessor', 'db_accessor']
    while services_not_up:
        try:
            service = services_not_up.pop(0)
            async with DaprClient() as client:
                response = await client.invoke_method(service, 'ping', 'PING')
            if response.text() != 'PONG':
                services_not_up.append(service)
        except DaprInternalError:
            logger.info(f'Service {service} not up, sleeping for {seconds} seconds')
            await asyncio.sleep(seconds)
    logger.info('All services up, proceeding')
