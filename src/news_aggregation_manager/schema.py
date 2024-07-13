from pydantic import BaseModel


class Tags(BaseModel):
    tags: str  # comma separated tags


class Message(BaseModel):
    pass


class Request(Message):
    recipient: str


class Response(Message):
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


class CreateDigestRequest(BaseModel):
    recipient: str = 'news_aggregation_manager'
    subject: str = 'create_digest'
    email: str


class UserSettings(BaseModel):
    max_sentences: int = 5
    max_news: int = 10
    info: str = ''
    tags: str = ''


class UserResponse(BaseModel):
    is_admin: bool = False
    contact_info: str = ''
    latest_news_processed: str = ''
    settings: UserSettings = UserSettings()


class News(BaseModel):
    summary: str | None = None
    title: str
    url: str
    id: int
    text: str
    publish_date: str


class NewNewsResponse(BaseModel):
    last_news_time: str
    news: list[News]


class CreateDigestAIRequest(Request):
    recipient: str = 'ai_accessor'
    subject: str = 'create_digest'
    user: UserResponse
    news: NewNewsResponse
    id: int


class DigestEntry(BaseModel):
    text: str
    url: str


class CreateDigestAIResponse(Response):
    recipient: str = 'news_aggregation_manager'
    subject: str = 'digest_result'
    digest: list[DigestEntry]
    id: int


class ReporterRequest(BaseModel):
    contact: str
    subject: str = 'report_ready'
    digest: list[DigestEntry]
