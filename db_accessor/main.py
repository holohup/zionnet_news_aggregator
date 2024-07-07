from pydantic_core import from_json
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from redis.exceptions import ConnectionError
import redis
import logging
import logging.config

from config import load_config
from repository import RedisUserRepository
from schema import User, UserWithEmail
from responses import (
    exists_response,
    created_response,
    exception_response,
    user_deleted_response,
    user_not_found,
    user_info_response
)


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
r = redis.Redis(config.redis.host, config.redis.port, decode_responses=True)
repo = RedisUserRepository(redis=r, prefix=config.storage.email_prefix)

app = App()


@app.method(name='create_user')
def create_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    user = UserWithEmail(**from_json(request.text()))
    logger.info(f'Received user creation request {user}')
    try:
        if repo.user_exists(user.email):
            logger.warning('User already exists')
            return InvokeMethodResponse(data=exists_response)
        repo.create_user(user)
    except ConnectionError as e:
        result = exception_response(str(e))
        logger.error(f'Exception: {str(e)}')
    else:
        result = created_response(user)
        logger.info('User created')
    return InvokeMethodResponse(data=result)


@app.method(name='delete_user')
def delete_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    user_email = request.text()
    logger.info(f'Received user DELETION request for {user_email}')
    try:
        if not repo.user_exists(user_email):
            logger.warning('User does not exist')
            return InvokeMethodResponse(data=user_not_found(user_email))
        repo.delete_user(user_email)
    except ConnectionError as e:
        result = exception_response(str(e))
        logger.error(f'Exception: {str(e)}')
    else:
        result = user_deleted_response
        logger.info('User deleted')
    return InvokeMethodResponse(data=result)


@app.method(name='get_user_info')
def get_user_info(request: InvokeMethodRequest) -> InvokeMethodResponse:
    user_email = request.text()
    logger.info(f'Received get user info request for {user_email}')
    try:
        if not repo.user_exists(user_email):
            logger.warning('User does not exist')
            return InvokeMethodResponse(data=user_not_found(user_email))
        user = repo.get_user(user_email)
    except ConnectionError as e:
        result = exception_response(str(e))
        logger.error(f'Exception: {str(e)}')
    else:
        result = user_info_response(user)
        logger.info(f'User data fetched: {result}')
    return InvokeMethodResponse(data=result)


if __name__ == '__main__':
    logger.info('Starting db_accessor')
    app.run(config.grpc.port)
