from typing import Optional

from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


class PasswordRequestForm(OAuth2PasswordRequestForm):
    """Class to simplify testing with Swagger, adds a email field."""

    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
        grant_type: str = Form(default=None, regex='password'),
        scope: str = Form(default=""),
        client_id: Optional[str] = Form(default=None),
        client_secret: Optional[str] = Form(default=None),
    ):
        super().__init__(
            grant_type=grant_type,
            username=username,
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )
        self.email = self.username
