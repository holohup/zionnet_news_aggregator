# The API gateway provides REST API for the service - it validates the requests, performs authorization and
# authentification, and makes sure the validated requests are forwarded to the right Managers

from fastapi import FastAPI
import logging.config
import logging

from schema import RegistrationRequest
from utils import obfuscate_password
from config import load_config
from user_manager import UserManager

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

app = FastAPI()
u_manager = UserManager(config.grpc.user_manager_app_id)


@app.post('/register')
async def register_new_user(request: RegistrationRequest):
    """User registration. After validation send a request to UserManager."""

    logger.info(f'Registering user: {request.email} {obfuscate_password(request.password)}')
    result = await u_manager.register_user(request.model_dump_json())

    return {'result': result}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
