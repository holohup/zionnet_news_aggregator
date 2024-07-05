from pydantic import BaseModel, EmailStr, field_validator, validate_email


class LowerEmailStr(EmailStr):
    """Convert email to lowercase right from the start to exclude duplicates."""

    @classmethod
    def validate(cls, value: EmailStr) -> EmailStr:
        email = validate_email(value)[1]
        return email.lower()


class RegistrationRequest(BaseModel):
    email: LowerEmailStr
    password: str

    @field_validator('password', mode='after')
    @classmethod
    def validate_password(cls, password, **kwargs):
        if not password:
            raise ValueError('Password can not be empy')
        return password
