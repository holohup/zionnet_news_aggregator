from pydantic import BaseModel


class Tags(BaseModel):
    tags: str  # comma separated tags


class Request(BaseModel):
    recipient: str


class Response(BaseModel):
    recipient: str


class UpdateNewsRequest(Request):
    subject: str = 'update_news'
    detail: Tags


class GenerateTagsRequest(Response):
    subject: str = 'generate_tags'
    id: int
    description: str
    max_tags: int


class GenerateTagsResponse(BaseModel):
    subject: str = 'tags_response'
    result: str
    id: int
