from pydantic import BaseModel


class BaseModelWithJSONString(BaseModel):

    @property
    def jsons(self) -> str:
        return self.model_dump_json()


class User(BaseModelWithJSONString):
    password: str
    settings: dict = {}


class UserWithEmail(User):
    email: str


class DB_Accessor_Response(BaseModelWithJSONString):
    result: str
    status_code: int
    detail: str | User
