import asyncio
import logging

from dapr.aio.clients import DaprClient

logger = logging.getLogger(__name__)


async def all_other_services_alive() -> bool:
    services = ['ai_accessor', 'ai_manager', 'db_accessor', 'news_accessor', 'tg_accessor', 'user_manager']
    results = await asyncio.gather(*[ping_service(service) for service in services])
    return all(results)


async def ping_service(service_name: str) -> bool:
    result = await grpc_response_text(service_name, 'ping', 'PING')
    return result == 'PONG'


async def grpc_response_text(app_id: str, method: str, data: str) -> dict:
    async with DaprClient() as client:
        response = await client.invoke_method(app_id, method, data)
    return response.text()
