import os
from dataclasses import dataclass
from datetime import timedelta

from dapr.clients import DaprClient

DEBUG = str(os.getenv('DEBUG', False)).lower() in ('true', 'yes', '1', 'debug')


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class StorageConfig:
    latest_update_filename: str
    news_filename: str
    latest_update_time_from_now_if_no_file_exists: int
    time_delta_seconds_to_avoid_collisions: int
    hours_of_news_to_return_if_user_has_no_news_read_yet: int


@dataclass
class ParsingConfig:
    max_entries: int
    news_expiration_hours: timedelta
    api_key: str
    max_query_chars: int


@dataclass
class GRPCSettings:
    port: int
    topic: str
    pubsub: str
    max_news_to_return: int


@dataclass
class Config:
    logging: LoggingConfig
    storage: StorageConfig
    parsing: ParsingConfig
    grpc: GRPCSettings
    service_name: str


def get_api_key(store_name: str, var: str):
    with DaprClient() as client:
        result = client.get_secret(store_name=store_name, key=var).secret[var]
    return result


def load_config():
    news_api_key_var = 'WORLD_NEWS_API_KEY'
    api_key = get_api_key('localsecretstore', news_api_key_var) if not DEBUG else os.getenv(news_api_key_var)
    return Config(
        logging=LoggingConfig(logging_config),
        storage=StorageConfig(
            latest_update_filename='news/latest_update.json',
            news_filename='news/news.json',
            latest_update_time_from_now_if_no_file_exists=24*2,
            time_delta_seconds_to_avoid_collisions=1,
            hours_of_news_to_return_if_user_has_no_news_read_yet=48
        ),
        parsing=ParsingConfig(
            max_entries=100, news_expiration_hours=timedelta(hours=24 * 7), api_key=api_key, max_query_chars=100
        ),
        grpc=GRPCSettings(topic='news_tasks', port=50052, pubsub='pubsub', max_news_to_return=700),
        service_name='news_accessor'
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
