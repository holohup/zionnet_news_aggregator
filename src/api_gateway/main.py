import logging
import logging.config
from typing import Annotated

from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse, Response


from config import load_config
from exceptions import admin_only_exception
from oauth_email import PasswordRequestForm
from schema import (RegistrationRequest, Token, TokenRequest,
                    UpdateUserSettingsRequest, User, UserSettings)
from service_pinger import all_other_services_alive
from utils import obfuscate_password
from news_aggregation_manager import News_Aggregation_Manager
from user_manager import UserManager

config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)

app: FastAPI = FastAPI(
    title='News Aggregator API',
    description='Use AI help to navigate through endless news about nothing, concentrate on real gems only.',
    version='1.0.0'
)
u_manager = UserManager(app_id=config.grpc.user_manager_app_id, token_config=config.jwt)
news_aggregation_manager = News_Aggregation_Manager(
    config.grpc.news_aggregation_manager_pubsub, config.grpc.news_aggregation_manager_topic
)


@app.post('/user/register')
async def register_new_user(request: RegistrationRequest) -> JSONResponse:
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
) -> JSONResponse:
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
async def delete_user(current_user: Annotated[User, Depends(u_manager.get_current_user)], user_email: str) -> None:
    """User deletion chain starting point."""

    logger.info(f'Deleting user: {user_email}')
    if not current_user.is_admin:
        logger.info('Not an admin request, skipping')
        raise admin_only_exception
    await u_manager.delete_user(user_email)
    return None


@app.post('/digest')
async def create_digest(current_user: Annotated[User, Depends(u_manager.get_current_user)]) -> JSONResponse:
    """Endpoint that launches the digest creation sequence."""

    logger.info(f'Received digest request for {current_user.email}')
    result = await news_aggregation_manager.create_digest(current_user)
    if result is None:
        return {'result': 'Your digest will be delivered shortly'}
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


@app.get('/user/info/{user_email}')
async def get_user_info(
    current_user: Annotated[User, Depends(u_manager.get_current_user)], user_email: str
) -> JSONResponse:
    """Get user info."""

    logger.info(f'Getting user info for {user_email}')
    if not current_user.is_admin:
        logger.info('Access to see user data denied due to lack of privileges')
        raise admin_only_exception
    result = await u_manager.get_user(user_email.lower())
    status_code = result.pop('status_code')
    return JSONResponse(content=result, status_code=status_code)


@app.post(
        '/login', summary='Hidden endpoint for Swagger auth integration',
        response_model=Token,
        include_in_schema=False
)
async def generate_token(req_data: PasswordRequestForm = Depends()) -> Token:
    """Create a token for FastAPI's Swagger UI"""

    email, password = req_data.email, req_data.password
    logger.info(f'Creating a token for {email}, {obfuscate_password(password)}')
    result = await u_manager.create_token(email, password)
    logger.info('Returning token')
    return result


@app.post('/token', summary='Token generation endpoint', response_model=Token)
async def create_token(request: TokenRequest) -> Token:
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
    """Info about current user."""

    logger.info('Servicing a get current user request.')
    return current_user


@app.get('/ping', include_in_schema=False)
async def ping_all_other_services() -> dict:
    """Pings 6 other services to check if they are up."""

    logger.info('Pinging all services')
    result = await all_other_services_alive()
    if not result:
        return {'error': 'something is not working'}
    return {'ok': 'all services up'}


if __name__ == '__main__':
    logger.info(f'Starting {config.service_name}')
    import uvicorn
    uvicorn.run(app=app, host='0.0.0.0', port=8000)
