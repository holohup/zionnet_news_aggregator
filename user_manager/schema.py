from dataclasses import dataclass


@dataclass
class UserManagerResponse:
    result: str
    status_code: int
    detail: str


@dataclass
class CreateUserManagerResponse(UserManagerResponse):
    pass
