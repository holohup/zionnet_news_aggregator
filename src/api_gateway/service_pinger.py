import asyncio
import logging

from dapr.aio.clients import DaprClient

logger = logging.getLogger(__name__)


async def all_other_services_alive() -> bool:
    """An utility decoupled from other services to check if all the services are up."""

    services = ['ai_accessor', 'news_aggregation_manager', 'db_accessor', 'news_accessor', 'tg_accessor', 'user_manager']
    results = await asyncio.gather(*[ping_service(service) for service in services])
    return all(results)


async def ping_service(service_name: str) -> bool:
    """Returns if the service is up or not."""

    result = await grpc_response_text(service_name, 'ping', 'PING')
    return result == 'PONG'


async def grpc_response_text(app_id: str, method: str, data: str) -> dict:
    """Special gRPC invoker without the try/except block, if the service  or dapr is down,
    will raise an error. It's a feature, since this code is part of the internal
    structure for integration tests. Not used by a user or any user scenarios."""

    async with DaprClient() as client:
        response = await client.invoke_method(app_id, method, data)
    return response.text()
