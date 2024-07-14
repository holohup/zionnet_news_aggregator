import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic_core import from_json
from schema import User, UserSettings, UserWithEmail

from redis import Redis

logger = logging.getLogger(__name__)


class UserRepository(ABC):
    """The abstract class - defines the interface for all Repositories."""

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

    @abstractmethod
    def update_settings(self, request: dict):
        pass

    @abstractmethod
    def get_password_hash(self, email: str) -> str:
        pass

    @abstractmethod
    def get_all_user_tags(self) -> str:
        pass

    @abstractmethod
    def update_timestamp(self, data: dict) -> User:
        pass


class RedisUserRepository(UserRepository):
    """A layer between the database and main to incapsulate the details."""

    def __init__(self, redis, prefix, admins: list[str]) -> None:
        self._r: Redis = redis
        self._prefix: str = prefix
        self._admins = admins

    def user_exists(self, email: str) -> bool:
        """Checks if the user with given email exists in the db."""

        return self._r.exists(self._prefix + email.lower())

    def create_user(self, user_with_email: UserWithEmail) -> User:
        """Creates a user."""

        dct = dict(user_with_email)
        email = dct.pop('email').lower()
        if email in self._admins:
            logger.warning(f'Creating an admin account for {email}')
            dct.update({'is_admin': True})
        user = User(**dct)
        self._r.set(self._prefix+email.lower(), user.jsons)
        return self.get_user(email)

    def delete_user(self, user_email: str):
        """Deletes the user given the email."""

        self._r.delete(self._prefix+user_email.lower())

    def get_user(self, email: str) -> User:
        """Given a email returns a user."""

        return User(**from_json(self._r.get(self._prefix+email.lower())))

    def update_settings(self, request: dict) -> User:
        """Updates users settings and returns the updated User."""

        email, settings = request['email'].lower(), request['settings']
        user = self.get_user(email)
        prev_settings = user.settings.model_copy()
        new_settings = {k: v if v else getattr(prev_settings, k) for k, v in settings.items()}
        new_settings = UserSettings.model_validate(new_settings)
        self._update_user_data(email, 'settings', new_settings)
        return self.get_user(email)

    def _update_user_data(self, email: str, field: str, value: Any):
        """Updates a specific user field with value.
        Since the user is stored in redis as a string, it deletes the old string
        and stores the new one with new params."""

        user: User = self.get_user(email.lower())
        setattr(user, field, value)
        new_user = UserWithEmail.model_validate({'email': email, **user.model_dump()})
        self.delete_user(email)
        self.create_user(new_user)

    def get_password_hash(self, email: str) -> str:
        """Gets the password hash for the user."""

        user: User = self.get_user(email)
        return user.password

    def get_all_user_tags(self) -> str:
        """Gathers all tags for the users into a single comma-separated string."""

        emails = self._get_all_emails()
        users = [self.get_user(email) for email in emails]
        unique_tags = {tag.strip().lower() for user in users for tag in user.settings.tags.split(',') if tag}
        logger.info(f'Tags ready: {unique_tags}')
        return ', '.join(sorted(unique_tags))

    def update_timestamp(self, data: dict) -> User:
        """Updates the user last read news timestamp."""

        self._update_user_data(data['email'], 'latest_news_processed', data['latest_update'])
        return self.get_user(data['email'])

    def _get_all_emails(self) -> list[str]:
        """Gets emails of all users stored in the db."""

        return [email.lstrip(self._prefix) for email in self._r.scan_iter(self._prefix+'*')]
