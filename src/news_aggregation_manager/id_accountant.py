import logging
from typing import NamedTuple

logger = logging.getLogger(__name__)


class AccountantEntry(NamedTuple):
    """What info about the user is to be stored."""

    contact_info: str
    latest_update: str
    email: str


class IDAccountant:
    """Creates id's and stores the data for the user.
    Needed to provide the id to create a message without unneeded data,
    and when the response with id is received to get the needed data to proceed
    with the request execution. Is injected into the processor."""

    def __init__(self) -> None:
        self._contacts = {}
        self._counter = 0

    def new_id(self, contact: str, latest_update: str, email: str) -> int:
        """Creates a new unique id and stores the data needed."""

        self._counter += 1
        self._contacts[self._counter] = AccountantEntry(contact_info=contact, latest_update=latest_update, email=email)
        return self._counter

    def __getitem__(self, id_) -> AccountantEntry | None:
        """Returns the data stored associated with the id_"""

        entry = self._contacts.get(id_)
        if not entry:
            logger.error(f'Received id request which is not valid: {id_}')
            return
        return entry
