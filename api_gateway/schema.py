from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    contact_info: str = ''
    info: str

    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, password, **kwargs):
        if not password:
            raise ValueError('Password can not be empy')
        return password

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "string",
                    "contact_info": "44040624",
                    "info": 'I am a junior programmer, I live in DC, I am interested in football and celebrities. I really love bikes, ski and swimming, but I prefer playing minecraft or BrawlStars all day.',
                }
            ]
        }
    }


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str
    is_admin: bool


class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class UserSettings(BaseModel):
    max_sentences: int | None = None
    max_news: int | None = None
    info: str | None = None
    tags: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "max_sentences": 5,
                    "max_news": 10,
                    "info": 'I am a junior programmer, I live in DC, I am interested in football and celebrities',
                    "tags": 'football, Ronaldo, Mark Knopfler',
                }
            ]
        }
    }


class User(BaseModel):
    email: str
    is_admin: bool
    contact_info: str
    latest_news_processed: str
    settings: UserSettings


class TokenPayload(BaseModel):
    email: str
    is_admin: bool
    exp: float


class UpdateUserSettingsRequest(BaseModel):
    email: str
    settings: UserSettings
