from dataclasses import dataclass, asdict


@dataclass
class ParseSettings:
    text: str = ''  # comma separated interests, e.g. 'tesla, Biden, covid'
    language: str = 'en'  # ISO 6391 language code
    source_countries: str = 'us, il'  # A comma-separated list of ISO 3166 country codes of news origin.
    sort: str = 'publish-time'
    number: int = 100  # results per page while parsing

    @property
    def dict(self):
        return asdict(self)
