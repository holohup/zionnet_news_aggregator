from typing import Callable, NamedTuple

from schema import CreateDigestAIResponse, CreateDigestRequest, Message


class MessageParser(NamedTuple):
    """Defines how a message is processed, depending on message subject"""

    model: type[Message]
    processor: Callable[[Message], None]


parse_details = {
    'create_digest': MessageParser(model=CreateDigestRequest, processor='process_create_digest_request'),
    'digest_result': MessageParser(model=CreateDigestAIResponse, processor='process_digest_result')
}
