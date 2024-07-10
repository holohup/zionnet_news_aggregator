from pydantic import BaseModel


class BaseModelWithJSONString(BaseModel):

    @property
    def jsons(self) -> str:
        return self.model_dump_json()


class UserSettings(BaseModelWithJSONString):
    max_sentences: int = 5
    max_news: int = 10
    info: str = ''
    tags: str = ''


class UserResponse(BaseModel):
    is_admin: bool = False
    contact_info: str = ''
    latest_news_processed: str = ''
    settings: UserSettings = UserSettings()


class User(BaseModelWithJSONString):
    password: str
    is_admin: bool = False
    contact_info: str = ''
    latest_news_processed: str = ''
    settings: UserSettings = UserSettings()


class UserWithEmail(User):
    email: str


class DB_Accessor_Response(BaseModelWithJSONString):
    result: str
    status_code: int
    detail: str | UserResponse
