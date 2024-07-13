import json
import logging

from dapr.aio.clients import DaprClient, DaprInternalError
from exceptions import http_exception, server_error

logger = logging.getLogger(__name__)


async def invoke_grpc_method(app_id: str, method: str, data: str) -> dict:
    try:
        async with DaprClient() as client:
            response = await client.invoke_method(app_id, method, data)
    except DaprInternalError as e:
        logger.error(str(e))
        return server_error
    result = json.loads(response.text())
    if result['result'] == 'error':
        logger.error(f'Error: {result["detail"]}')
        raise http_exception(result)
    return result


async def publish_message(pubsub_name: str, topic_name: str, data):
    try:
        async with DaprClient() as client:
            await client.publish_event(pubsub_name=pubsub_name, topic_name=topic_name, data=data)
    except DaprInternalError as e:
        logger.exception(f'Something is not right with Dapr: {e}')
        return server_error
    except Exception as e:
        logger.exception(e)
        return server_error
