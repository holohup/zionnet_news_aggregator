import json
import logging
import logging.config

from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse

from config import load_config
from db_accessor import DB_Accessor
from security import replace_password_with_hash_in_user_data
from utils import parse_data


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
app = App()
db_accessor = DB_Accessor(config.grpc.db_accessor_app_id)


@app.method(name='register_user')
def register_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    data = replace_password_with_hash_in_user_data(request.text())
    logger.info(f'Received registration request for {json.loads(data)["email"]}')
    result = db_accessor.create_user(data)
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=result)


@app.method(name='delete_user')
def delete_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    email = request.text()
    logger.info(f'Received deletion request for {email}')
    result = db_accessor.delete_user(email)
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=result)


@app.method(name='get_user')
def get_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    email = request.text()
    logger.info(f'Getting user info for {email}')
    result = db_accessor.get_user(email)
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=result)


@app.method(name='create_token')
def create_token(request: InvokeMethodRequest) -> InvokeMethodResponse:
    logger.info('Received token creation request')
    result = db_accessor.create_token(request.text(), config.jwt)
    logger.info('Token generated')
    return InvokeMethodResponse(data=result)


if __name__ == '__main__':

    logger.info('Starting UserManager')
    app.run(50051)




