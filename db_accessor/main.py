import json
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from redis.exceptions import ConnectionError
from http import HTTPStatus
import redis
import logging
import logging.config

from config import load_config
from repository import RedisUserRepository
from schema import DB_Accessor_Response, User
from responses import exists_response, created_response, exception_response

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
r = redis.Redis(config.redis.host, config.redis.port, decode_responses=True)
repo = RedisUserRepository(redis=r, prefix=config.storage.email_prefix)


app = App()


@app.method(name='create_user')
def create_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    user_info = json.loads(request.text())
    logger.info(f'Received user creation request {user_info}')
    if repo.user_exists(user_info['email']):
        logger.warning('User already exists')
        return InvokeMethodResponse(data=exists_response.json)
    try:
        repo.create_user(User(**user_info))
    except ConnectionError as e:
        result = exception_response(str(e))
        logger.error(f'Exception: {str(e)}')
    else:
        result = created_response(user_info)
        logger.info('User created')
    return InvokeMethodResponse(data=result.json)


if __name__ == '__main__':
    logger.info('Starting db_accessor')
    app.run(50052)
