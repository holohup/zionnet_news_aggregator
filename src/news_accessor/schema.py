from dataclasses import asdict, dataclass

from pydantic import BaseModel


@dataclass
class ParseSettings:
    text: str = ''  # comma separated interests, e.g. 'tesla, Biden, covid'
    language: str = 'en'  # ISO 6391 language code
    source_countries: str = 'US, IL'  # A comma-separated list of ISO 3166 country codes of news origin.
    sort: str = 'publish-time'
    sort_direction: str = 'DESC'
    number: int = 100  # results per page while parsing

    @property
    def dict(self):
        return asdict(self)


class Tags(BaseModel):
    tags: str  # comma separated tags


class Request(BaseModel):
    recipient: str


class UpdateNewsRequest(Request):
    subject: str = 'update_news'
    detail: Tags


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
