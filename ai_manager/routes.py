from schema import CreateDigestAIResponse, CreateDigestRequest, Message
from typing import Callable, NamedTuple


class MessageParser(NamedTuple):
    model: type[Message]
    processor: Callable[[Message], None]


parse_details = {
    'create_digest': MessageParser(model=CreateDigestRequest, processor='process_create_digest_request'),
    'digest_result': MessageParser(model=CreateDigestAIResponse, processor='process_digest_result')
}
