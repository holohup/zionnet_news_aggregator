from abc import ABC, abstractmethod

from pydantic_core import from_json
from redis import Redis

from schema import User, UserWithEmail


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

    def __init__(self, redis, prefix) -> None:
        self._r: Redis = redis
        self._prefix: str = prefix

    def user_exists(self, email: str) -> bool:
        return self._r.exists(self._prefix + email.lower())

    def create_user(self, user_with_email: UserWithEmail):
        dct = dict(user_with_email)
        email = dct.pop('email')
        user = User(**dct)
        self._r.set(self._prefix+email.lower(), user.jsons)
        return self.get_user(email)

    def delete_user(self, user_email: str):
        self._r.delete(self._prefix+user_email.lower())

    def get_user(self, email: str):
        return User(**from_json(self._r.get(self._prefix+email.lower())))

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
