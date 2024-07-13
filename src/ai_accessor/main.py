import asyncio
import json
import logging
import logging.config
import threading

from ai_services import AI
from cloudevents.sdk.event import v1
from config import DEBUG, configure_env_variables, load_config
from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from schema import (CreateDigestAIRequest, CreateDigestAIResponse, DigestEntry,
                    GenerateTagsRequest, GenerateTagsResponse)
from semantic_kernel import Kernel

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

kernel = Kernel()
app = App()

loop = asyncio.new_event_loop()


async def generate_tags(data):
    logger.info('Generating tags')
    request = GenerateTagsRequest.model_validate(data)
    result = await ai.generate_tags(description=request.description, maximum_tags=request.max_tags)
    logger.info('Result ready')
    response = GenerateTagsResponse(result=str(result), id=request.id, recipient='user_manager')
    with DaprClient() as client:
        client.publish_event(config.grpc.pubsub, config.grpc.topic, response.model_dump_json())


async def create_digest(data):
    logger.info('Creating a digest')
    request = CreateDigestAIRequest.model_validate(data)
    result = await ai.generate_digest(request)
    response = CreateDigestAIResponse(digest=result, id=request.id)
    logger.info('Digest ready')
    with DaprClient() as client:
        client.publish_event(config.grpc.pubsub, config.grpc.topic, response.model_dump_json())


executors = {
    'generate_tags': generate_tags,
    'create_digest': create_digest
}


async def process_event(data: dict):
    subject = data['subject']
    executor = executors.get(subject)
    if not executor:
        return
    logger.info(f'Executor for {subject} found, proceeding')
    await executors[subject](data)


@app.subscribe(pubsub_name=config.grpc.pubsub, topic=config.grpc.topic)
def task_consumer(event: v1.Event) -> None:
    data = json.loads(event.Data())
    logger.info('Received event')
    if data.get('recipient') != 'ai_accessor':
        logger.info('Not for ai_accessor')
        return
    future = asyncio.run_coroutine_threadsafe(process_event(data), loop)
    future.result()


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
    await asyncio.Event().wait()

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
