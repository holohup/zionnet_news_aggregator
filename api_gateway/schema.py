from pydantic import BaseModel, EmailStr, field_validator


class RegistrationRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, password, **kwargs):
        if not password:
            raise ValueError('Password can not be empy')
        return password


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str


class TokenRequest(RegistrationRequest):
    pass