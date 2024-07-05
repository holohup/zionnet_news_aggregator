from typing import NamedTuple
import json


class DB_Accessor_Response(NamedTuple):
    result: str
    status_code: int
    detail: str

    @property
    def json(self) -> str:
        return json.dumps(self._asdict())


class User(NamedTuple):
    email: str
    password: str
    settings: dict = {}
