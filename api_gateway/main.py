# The API gateway provides REST API for the service - it validates the requests, performs authorization and
# authentification, and makes sure the validated requests are forwarded to the right Managers

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse, Response
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


@app.post('/user/register')
async def register_new_user(request: RegistrationRequest):
    """User registration. After validation send a request to UserManager."""

    logger.info(f'Registering user: {request.email} {obfuscate_password(request.password)}')
    result = await u_manager.register_user(request.model_dump_json())
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


@app.delete('/user/delete/{user_email}', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_user(user_email: str):
    """User deletion chain starting point."""

    logger.info(f'Deleting user: {user_email}')
    await u_manager.delete_user(user_email)
    return None


@app.get('/user/info/{user_email}')
async def get_user_info(user_email: str):
    """Get user info."""

    result = await u_manager.get_user(user_email)
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


if __name__ == '__main__':
    logger.info('Starting API Gateway')
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
