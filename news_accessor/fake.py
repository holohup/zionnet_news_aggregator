from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NewsEntry(BaseModel):
    summary: str
    image: str
    sentiment: float
    author: str
    language: str
    video: Optional[str]
    title: str
    url: str
    source_country: str
    id: int
    text: str
    publish_date: datetime
    authors: List[str]

class Response(BaseModel):
    available: int
    news: list[NewsEntry]

news_entries = [
    NewsEntry(
        summary="And shoppers say they’re ideal for “year-round” wear",
        image="https://people.com/thmb/UNgAhXtTJDCa-YWte6tIYHml7iM=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc():focal(2999x0:3001x2)/week-2---linen-pants-amazon-one-off-tout-517c354890f548d4a35333a7098100d8.jpg",
        sentiment=0.519,
        author="Madison Yauger",
        language="en",
        video=None,
        title="These ‘Versatile’ Linen-Blend Pants with a Celebrity-Worn Detail Are on Sale in 16 Colors",
        url="https://people.com/anrabess-linen-palazzo-pants-deal-amazon-july-2024-8673295",
        source_country="US",
        id=248985898,
        text="Paperbag",
        publish_date="2024-07-08 12:00:00",
        authors=["Madison Yauger"]
    ),
    NewsEntry(
        summary="Over the past year, Sonny Angel — a biblically inaccurate, 3-inch-tall cherub figurine with peculiar headgear — has taken over the hearts, minds, phones, display shelves, and nightstands of collectors across the world. The plastic dolls, wearing helmets ranging in form from pancakes to sunflowers, are garnering millions of views on TikTok and Instagram, popping [&#8230;]",
        image="https://platform.vox.com/wp-content/uploads/sites/2/2024/06/shutterstock_1403600030_full.jpg?quality=90&strip=all&crop=0%2C10.76363770124%2C100%2C78.472724597521&w=1200",
        sentiment=0.273,
        author="Alex Abad-Santos",
        language="en",
        video=None,
        title="This tiny doll is making everyone so happy",
        url="https://www.vox.com/culture/357364/sonny-angel-hippers-shortage-explained",
        source_country="us",
        id=249021106,
        text="Over the past",
        publish_date="2024-07-08 12:00:00",
        authors=["Alex Abad-Santos"]
    )
]

def resp():
    return Response(available=10, news=news_entries)




with open('1.txt', 'w') as file:
    file.write('111')
    file.write('\n')

