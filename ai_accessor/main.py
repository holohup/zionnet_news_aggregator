import threading
from cloudevents.sdk.event import v1
import asyncio
import logging
import logging.config
from dapr.clients.exceptions import DaprInternalError
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
import json
from semantic_kernel import Kernel
from ai_services import AI
from schema import GenerateTagsRequest, GenerateTagsResponse
from config import load_config, configure_env_variables, DEBUG
from dapr.clients import DaprClient

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

kernel = Kernel()
app = App()

loop = asyncio.new_event_loop()


async def process_event(data: dict):
    logger.info('Generating tags')
    request = GenerateTagsRequest.model_validate(data)
    result = await ai.generate_tags(description=request.description, maximum_tags=request.max_tags)
    logger.info('Result ready')
    response = GenerateTagsResponse(result=str(result), id=request.id)
    with DaprClient() as client:
        client.publish_event(config.grpc.pubsub, config.grpc.topic, response.model_dump_json())


@app.subscribe(pubsub_name=config.grpc.pubsub, topic=config.grpc.topic)
def task_consumer(event: v1.Event) -> None:
    data = json.loads(event.Data())
    logger.info(f'Received event: {data}')
    if data.get('subject') == 'generate_tags':
        future = asyncio.run_coroutine_threadsafe(process_event(data), loop)
        future.result()  # Wait for the coroutine to finish to catch any exceptions


@app.method('ping')
def ping_service(request: InvokeMethodRequest) -> InvokeMethodResponse:
    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')


def run_app():
    app.run(config.grpc.port)


def start_event_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


async def main():
    grpc_thread = threading.Thread(target=run_app, daemon=True)
    grpc_thread.start()
    loop_thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
    loop_thread.start()
    await asyncio.Event().wait()  # Keep the main loop running

if __name__ == '__main__':
    logger.info('Starting AIManager')
    if not DEBUG:
        try:
            configure_env_variables(config.secrets.store_name)
        except DaprInternalError as e:
            logger.error(f'Could not connect to the secrets store. Terminating. {str(e)}')
            raise
    ai = AI(kernel, config.ai)
    asyncio.run(main())
