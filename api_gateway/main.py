# The API gateway provides REST API for the service - it validates the requests, performs authorization and
# authentification, and makes sure the validated requests are forwarded to the right Managers

from typing import Annotated

from fastapi import FastAPI, status, Depends
from fastapi.responses import JSONResponse, Response

import logging.config
import logging

from exceptions import admin_only_exception
from schema import RegistrationRequest, Token, TokenRequest, User, UserSettings, UpdateUserSettingsRequest
from utils import obfuscate_password
from config import load_config
from oauth_email import PasswordRequestForm
from user_manager import UserManager
from ai_manager import AI_Manager

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(
    title='News Aggregator API',
    description='Use AI help to navigate through endless news about nothing, concentrate on real gems only.',
    version='1.0.0'
)
u_manager = UserManager(app_id=config.grpc.user_manager_app_id, token_config=config.jwt)
ai_manager = AI_Manager(config)


@app.post('/user/register')
async def register_new_user(request: RegistrationRequest):
    """User registration. After validation send a request to UserManager."""

    logger.info(
        f'Registering user: {request.email} {obfuscate_password(request.password)}'
    )
    result = await u_manager.register_user(request)
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


@app.patch('/user/update_settings')
async def update_user_settings(
    settings: UserSettings,
    current_user: Annotated[User, Depends(u_manager.get_current_user)]
):
    """Patch endpoint to update user settings."""

    settings = settings.model_dump(exclude_unset=True)
    email = current_user.email
    logger.info(f'Updating settings for {email}')
    request = UpdateUserSettingsRequest(settings=UserSettings.model_validate(settings), email=email)
    result = await u_manager.update_settings(request)
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


@app.delete(
    '/user/delete/{user_email}',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_user(current_user: Annotated[User, Depends(u_manager.get_current_user)], user_email: str):
    """User deletion chain starting point."""

    logger.info(f'Deleting user: {user_email}')
    if not current_user.is_admin:
        logger.info('Not an admin request, skipping')
        raise admin_only_exception
    await u_manager.delete_user(user_email)
    return None


@app.post('/digest')
async def create_digest(current_user: Annotated[User, Depends(u_manager.get_current_user)]):
    # """Endpoint that launches the digest creation sequence."""

    logger.info(f'Received digest request for {current_user.email}')
    await ai_manager.create_digest(current_user)
    return {'result': 'Your digest will be delivered shortly.'}


@app.get('/user/info/{user_email}')
async def get_user_info(current_user: Annotated[User, Depends(u_manager.get_current_user)], user_email: str):
    """Get user info."""

    logger.info(f'Getting user info for {user_email}')
    if not current_user.is_admin:
        logger.info('Access to see user data denied due to lack of privileges')
        raise admin_only_exception
    result = await u_manager.get_user(user_email)
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


@app.post('/login', summary='Hidden endpoint for Swagger auth integration', response_model=Token, include_in_schema=False)
async def generate_token(req_data: PasswordRequestForm = Depends()) -> Token:
    """Create a token for Swagger UI"""

    email, password = req_data.email, req_data.password
    logger.info(f'Creating a token for {email}, {obfuscate_password(password)}')
    result = await u_manager.create_token(email, password)
    logger.info('Returning token')
    return result


@app.post('/token', summary='Token generation endpoint', response_model=Token)
async def create_token(request: TokenRequest):
    """Create a token given valid email and password, or return an error."""
    email, password = request.email, request.password
    logger.info(f'Creating a token for {email}, {obfuscate_password(password)}')
    result = await u_manager.create_token(email, password)
    logger.info('Returning token')
    return result


@app.get('/user/me/', response_model=User)
async def read_users_me(
    current_user: Annotated[dict, Depends(u_manager.get_current_user)],
) -> User:
    logger.info('Servicing a get current user request.')
    return current_user


if __name__ == '__main__':
    logger.info('Starting API Gateway')
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
