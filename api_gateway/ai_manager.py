import logging

from schema import User

logger = logging.getLogger(__name__)


class AI_Manager:
    def __init__(self, config) -> None:
        self._config = config

    async def create_digest(self, user: User):
        pass
