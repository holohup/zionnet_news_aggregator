from dataclasses import asdict
import json
import logging
import logging.config
from http import HTTPStatus

from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse

from config import load_config
from db_accessor import DB_Accessor
from schema import CreateUserManagerResponse

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
app = App()
db_accessor = DB_Accessor(config.grpc.db_accessor_app_id)


@app.method(name='register_user')
def register_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    data = json.loads(request.text())
    logger.info(f'Received registration request for {data["email"]}')
    result = db_accessor.create_user(request.text())
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=json.dumps(result))


@app.method(name='delete_user')
def delete_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    data = request.text()
    logger.info(f'Received deletion request for {data}')
    result = db_accessor.delete_user(data)
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=json.dumps(result))


if __name__ == '__main__':
    logger.info('Starting UserManager')
    app.run(50051)
