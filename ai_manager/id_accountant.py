import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)


class AccountantEntry(NamedTuple):
    contact_info: str
    latest_update: str
    email: str


class IDAccountant:
    def __init__(self) -> None:
        self._contacts = {}
        self._counter = 0

    def new_id(self, contact: str, latest_update: str, email: str) -> int:
        self._counter += 1
        self._contacts[self._counter] = AccountantEntry(contact_info=contact, latest_update=latest_update, email=email)
        return self._counter

    def __getitem__(self, id_) -> AccountantEntry | None:
        entry = self._contacts.get(id_)
        if not entry:
            logger.error(f'Received id request which is not valid: {id_}')
            return
        return entry
