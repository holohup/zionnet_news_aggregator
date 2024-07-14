import logging

logger = logging.getLogger(__name__)


class IDAccountant:
    """Simple email storage to save ids and emails for async work."""

    def __init__(self) -> None:
        self._emails = {}
        self._counter = 0

    def new_id(self, email: str) -> int:
        """Creates a new id and stores the email associated with it."""

        self._counter += 1
        self._emails[self._counter] = email
        return self._counter

    def __getitem__(self, id_) -> str:
        """Returns the email associated with the id."""

        email = self._emails.get(id_)
        if not email:
            logger.error(f'Received id request which is not valid: {id_}')
        else:
            return email
