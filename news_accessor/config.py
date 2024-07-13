import os
from dataclasses import dataclass
from datetime import timedelta

from dapr.clients import DaprClient

DEBUG = str(os.getenv('DEBUG', False)).lower() in ('true', 'yes', '1', 'debug')


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class FilenamesConfig:
    latest_update_filename: str
    news_filename: str


@dataclass
class ParsingConfig:
    max_entries: int
    news_expiration_hours: timedelta
    api_key: str


@dataclass
class GRPCSettings:
    port: int
    topic: str
    pubsub: str


@dataclass
class Config:
    logging: LoggingConfig
    filenames: FilenamesConfig
    parsing: ParsingConfig
    grpc: GRPCSettings


def get_api_key(store_name: str, var: str):
    with DaprClient() as client:
        result = client.get_secret(store_name=store_name, key=var).secret[var]
    return result


def load_config():
    news_api_key_var = 'WORLD_NEWS_API_KEY'
    api_key = get_api_key('localsecretstore', news_api_key_var) if not DEBUG else os.getenv(news_api_key_var)
    return Config(
        logging=LoggingConfig(logging_config),
        filenames=FilenamesConfig(latest_update_filename='news/latest_update.json', news_filename='news/news.json'),
        parsing=ParsingConfig(max_entries=100, news_expiration_hours=timedelta(hours=24), api_key=api_key),
        grpc=GRPCSettings(topic='news_tasks', port=50052, pubsub='pubsub')
    )


# log info messages to stdout and file everything from debug

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '#[%(asctime)s] #%(levelname)-8s %(filename)s:'
            '%(lineno)d - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'log/news_accessor.log',
            'mode': 'a',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },
    'root': {'level': 'DEBUG', 'handlers': ['default', 'file']},
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
