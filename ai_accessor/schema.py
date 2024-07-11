from pydantic import BaseModel


class Request(BaseModel):
    recipient: str


class Response(BaseModel):
    recipient: str


class GenerateTagsRequest(Request):
    subject: str = 'generate_tags'
    id: int
    description: str
    max_tags: int


class GenerateTagsResponse(Response):
    subject: str = 'tags_response'
    result: str
    id: int
