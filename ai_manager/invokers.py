import logging
import json
from dapr.aio.clients import DaprClient, DaprInternalError
from dapr.ext.grpc import InvokeMethodResponse

logger = logging.getLogger(__name__)

server_error = {
    'result': 'error',
    'status_code': 500,
    'detail': 'Internal server error, check NewsManager logs',
}


async def invoke_method(app_id: str, method: str, data: str) -> str:
    try:
        async with DaprClient() as client:
            response: InvokeMethodResponse = await client.invoke_method(
                app_id, method, data
            )
    except DaprInternalError as e:
        logger.exception(str(e))
        return json.dumps(server_error)
    return response.text()


async def publish_message(pubsub_name: str, topic_name: str, data: dict):
    try:
        async with DaprClient() as client:
            await client.publish_event(pubsub_name=pubsub_name, topic_name=topic_name, data=json.dumps(data))
    except DaprInternalError as e:
        logger.exception(e)
