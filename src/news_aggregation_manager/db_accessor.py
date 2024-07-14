import json
import logging

from invokers import invoke_method_sync
from schema import UserResponse

logger = logging.getLogger(__name__)


class DB_Accessor:
    """Provides an interface to the db_accessor microservice."""

    def __init__(self, db_app_id: str):
        self._db_app_id = db_app_id

    def get_user(self, email: str) -> UserResponse | None:
        """Get a user given an email"""

        user_response = json.loads(invoke_method_sync(self._db_app_id, 'get_user_info', email))
        if user_response['result'] == 'error':
            logger.error(f'Could not get user from db_accessor: {user_response}')
            return None
        user = UserResponse.model_validate(user_response['detail'])
        logger.info(f'Fetched user: {user}')
        return user

    def update_last_news_time(self, email: str, latest_update_time: str) -> dict | None:
        """Updates users last news read timestamp."""

        request = {'email': email, 'latest_update': latest_update_time}
        response = json.loads(invoke_method_sync(self._db_app_id, 'update_time', json.dumps(request)))
        if response['result'] == 'error':
            logger.error('Could not update db')
            return response
        return None
