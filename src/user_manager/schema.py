from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class UserManagerResponse:
    result: str
    status_code: int
    detail: str


class RegistrationRequest(BaseModel):
    email: str
    password: str
    contact_info: str = ''
    info: str


class UserRegistrationSettings(BaseModel):
    max_sentences: int = 3
    max_news: int = 10
    info: str = ''
    tags: str = ''


class UserWithoutPassword(BaseModel):
    is_admin: bool = False
    contact_info: str = ''
    latest_news_processed: str = ''
    settings: UserRegistrationSettings = UserRegistrationSettings()


class User(UserWithoutPassword):
    password: str


class UserWithEmail(User):
    email: str


class Request(BaseModel):
    recipient: str


class Response(BaseModel):
    recipient: str


class GenerateTagsRequest(Request):
    subject: str = 'generate_tags'
    id: int
    description: str
    max_tags: int


class GenerateTagsResponse(Response):
    subject: str = 'tags_response'
    result: str
    id: int


class UserSettings(BaseModel):
    max_sentences: int | None = None
    max_news: int | None = None
    info: str | None = None
    tags: str | None = None


class UpdateUserSettingsRequest(BaseModel):
    email: str
    settings: UserSettings
