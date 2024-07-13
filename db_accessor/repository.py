import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic_core import from_json
from schema import User, UserSettings, UserWithEmail

from redis import Redis

logger = logging.getLogger(__name__)


class UserRepository(ABC):

    @abstractmethod
    def user_exists(self, email: str) -> bool:
        pass

    @abstractmethod
    def create_user(self, user: User):
        pass

    @abstractmethod
    def delete_user(self, user_email: str):
        pass

    @abstractmethod
    def get_user(self, email: str):
        pass


class RedisUserRepository(UserRepository):
    """A layer between the database and main to incapsulate the details."""

    def __init__(self, redis, prefix, admins: list[str]) -> None:
        self._r: Redis = redis
        self._prefix: str = prefix
        self._admins = admins

    def user_exists(self, email: str) -> bool:
        return self._r.exists(self._prefix + email.lower())

    def create_user(self, user_with_email: UserWithEmail):
        dct = dict(user_with_email)
        email = dct.pop('email').lower()
        if email in self._admins:
            logger.warning(f'Creating an admin account for {email}')
            dct.update({'is_admin': True})
        user = User(**dct)
        self._r.set(self._prefix+email.lower(), user.jsons)
        return self.get_user(email)

    def delete_user(self, user_email: str):
        self._r.delete(self._prefix+user_email.lower())

    def get_user(self, email: str):
        return User(**from_json(self._r.get(self._prefix+email.lower())))

    def update_settings(self, request: dict):

        email, settings = request['email'].lower(), request['settings']
        user = self.get_user(email)
        prev_settings = user.settings.model_copy()
        new_settings = {k: v if v else getattr(prev_settings, k) for k, v in settings.items()}
        new_settings = UserSettings.model_validate(new_settings)
        self._update_user_data(email, 'settings', new_settings)
        return self.get_user(email)

    def _update_user_data(self, email: str, field: str, value: Any):
        user: User = self.get_user(email.lower())
        setattr(user, field, value)
        new_user = UserWithEmail.model_validate({'email': email, **user.model_dump()})
        self.delete_user(email)
        self.create_user(new_user)

    def get_password_hash(self, email: str) -> str:
        user: User = self.get_user(email)
        return user.password

    def get_all_user_tags(self) -> str:
        emails = self._get_all_emails()
        users = [self.get_user(email) for email in emails]
        unique_tags = {tag.strip().lower() for user in users for tag in user.settings.tags.split(',') if tag}
        logger.info(f'Tags ready: {unique_tags}')
        return ', '.join(sorted(unique_tags))

    def update_timestamp(self, data: dict) -> User:
        self._update_user_data(data['email'], 'latest_news_processed', data['latest_update'])
        return self.get_user(data['email'])

    def _get_all_emails(self) -> list[str]:
        return [email.lstrip(self._prefix) for email in self._r.scan_iter(self._prefix+'*')]

    # def store(self, k: str, v: str):
    #     self._r.set(k, json.dumps(v))

    # def fetch_single_value(self, k: str):
    #     value = self._r.get(k)
    #     if value:
    #         return json.loads(str(value))
    #     return None

    # def store_to_set(self, k: str, v: list):
    #     items = [json.dumps(item) for item in v]
    #     self._r.sadd(k, *items)

    # def fetch_list_by_key(self, k: str):
    #     return self._r.smembers(k)

    # def key_exists(self, k: str):
    #     return self._r.exists(k)

    # def drop_by_prefix(self, prefix: str):
    #     for key in self._r.scan_iter(prefix + '*'):
    #         self._r.delete(key)

    # def list_all_available_keys(self) -> list[str]:
    #     return self._r.keys('*')
