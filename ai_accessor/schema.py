from pydantic import BaseModel


class GenerateTagsRequest(BaseModel):
    subject: str = 'generate_tags'
    id: int
    description: str
    max_tags: int


class GenerateTagsResponse(BaseModel):
    subject: str = 'tags_response'
    result: str
    id: int
