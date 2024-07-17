from typing import NamedTuple


class DigestItem(NamedTuple):
    """Digest item - text + url."""

    text: str
    url: str


class UserMessage(NamedTuple):
    """User message - chat id to send to and the digest."""

    chat_id: int
    digest: list[DigestItem]
