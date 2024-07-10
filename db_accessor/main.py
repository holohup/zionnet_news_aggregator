from typing import Any
from pydantic_core import from_json
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse
from redis.exceptions import ConnectionError
import redis
import logging
import logging.config

from config import load_config
from repository import RedisUserRepository
from schema import DB_Accessor_Response, User, UserWithEmail
from responses import (
    exists_response,
    created_response,
    exception_response,
    hash_response,
    user_deleted_response,
    user_not_found,
    user_info_response
)


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
r = redis.Redis(config.redis.host, config.redis.port, decode_responses=True)
repo = RedisUserRepository(redis=r, prefix=config.storage.email_prefix, admins=config.admins.admin_emails)

app = App()


@app.method(name='create_user')
def create_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    user = UserWithEmail(**from_json(request.text()))
    return invoke_method(user.email, 'create_user', user, created_response, creating=True)


@app.method(name='delete_user')
def delete_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    email = request.text()
    return invoke_method(email, 'delete_user', email, user_deleted_response)


@app.method(name='get_user_info')
def get_user_info(request: InvokeMethodRequest) -> InvokeMethodResponse:
    email = request.text()
    return invoke_method(email, 'get_user', email, user_info_response)


@app.method(name='update_user_settings')
def update_user_settings(request: InvokeMethodRequest) -> InvokeMethodResponse:
    settings_request = from_json(request.text())
    email = settings_request['email']
    return invoke_method(email, 'update_settings', settings_request, user_info_response)


@app.method(name='get_password_hash')
def get_password_hash(request: InvokeMethodRequest) -> InvokeMethodResponse:
    email = request.text()
    return invoke_method(email, 'get_password_hash', email, hash_response)


def invoke_method(
        email: str, method: str, attrs: Any, response: DB_Accessor_Response, creating: bool = False
) -> InvokeMethodResponse:
    logging.info(f'Trying to execute {method} for {email}')
    try:
        if creating and repo.user_exists(email):
            logger.warning('User already exists')
            return InvokeMethodResponse(data=exists_response)
        if not creating and not repo.user_exists(email):
            logger.warning(f'User {email} does not exist')
            return InvokeMethodResponse(data=user_not_found(email))
        result = getattr(repo, method)(attrs)
    except ConnectionError as e:
        resp = exception_response(str(e))
        logger.error(f'Exception: {str(e)}')
    else:
        resp = response(result)
        logger.info('Executed successfully.')
    return InvokeMethodResponse(data=resp)


if __name__ == '__main__':
    logger.info('Starting db_accessor')
    app.run(config.grpc.port)
