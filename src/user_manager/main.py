import json
import logging
import logging.config

from cloudevents.sdk.event import v1
from dapr.ext.grpc import App, InvokeMethodRequest, InvokeMethodResponse

from ai_accessor import AI_Accessor
from config import load_config
from db_accessor import DB_Accessor
from id_accountant import IDAccountant
from schema import (GenerateTagsResponse, RegistrationRequest,
                    UpdateUserSettingsRequest, UserSettings)
from security import replace_password_with_hash_in_user_data


config = load_config()
logging.config.dictConfig(config.logging.settings)
logger = logging.getLogger(__name__)
app = App()
accountant = IDAccountant()
ai_accessor = AI_Accessor(max_tags=config.max_tags, config=config.grpc)
db_accessor = DB_Accessor(
    config.grpc.db_accessor_app_id, accountant=accountant, ai_accessor=ai_accessor
)


@app.method(name='register_user')
def register_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """User registration."""

    data = replace_password_with_hash_in_user_data(request.text())
    user = RegistrationRequest.model_validate(data)
    logger.info(f'Received registration request for {user.email}')
    result = db_accessor.create_user(user)
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=result)


@app.method(name='delete_user')
def delete_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """User deletion."""

    email = request.text()
    logger.info(f'Received deletion request for {email}')
    result = db_accessor.delete_user(email)
    logger.info(f'Sending result {result}')
    return InvokeMethodResponse(data=result)


@app.method(name='get_user')
def get_user(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Get user."""

    email = request.text()
    logger.info(f'Getting user info for {email}')
    result = db_accessor.get_user(email)
    logger.info('Sending result')
    return InvokeMethodResponse(data=result)


@app.method(name='update_settings')
def update_settings(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Update settings."""

    data = request.text()
    logger.info('Updating settings.')
    result = db_accessor.update_settings(data)
    logger.info('Sending result')
    return InvokeMethodResponse(data=result)


@app.method(name='create_token')
def create_token(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Create a token."""

    logger.info('Received token creation request')
    result = db_accessor.create_token(request.text(), config.jwt)
    logger.info('Token generated')
    return InvokeMethodResponse(data=result)


@app.subscribe(config.grpc.pubsub, config.grpc.topic)
def updates_from_ai(event: v1.Event) -> None:
    """Subscribe to the messages, needed to get tags generation results to save them."""

    data = json.loads(event.Data())
    logger.info('Received event')
    if data.get('subject') != 'tags_response':
        logger.info(f'Not for {config.service_name}')
        return
    response = GenerateTagsResponse.model_validate(data)
    email = accountant[response.id]
    logger.info(f'Saving new tags for {email}')
    if not email:
        return
    request = UpdateUserSettingsRequest(
        email=email, settings=UserSettings(tags=response.result)
    )
    db_accessor.update_settings(request.model_dump_json())


@app.method('ping')
def ping_service(request: InvokeMethodRequest) -> InvokeMethodResponse:
    """Returns a PONG when pinged."""

    logger.info('Received PING, returning PONG')
    return InvokeMethodResponse(data='PONG')


if __name__ == '__main__':
    logger.info(f'Starting {config.service_name}')
    app.run(config.grpc.port)
