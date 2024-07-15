import os
from dataclasses import dataclass

from dapr.clients import DaprClient


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class ServiceConfig:
    pubsub: str
    topic: str
    app_id: str


@dataclass
class BotConfig:
    token: str
    max_text_length: int
    pause_seconds_between_messages: str


@dataclass
class Config:
    logging: LoggingConfig
    service: ServiceConfig
    bot: BotConfig
    grpc_port: int
    service_name: str


def fetch_token(store_name):
    debug = str(os.getenv('DEBUG', False)).lower() in ('true', 'yes', 'debug')
    if debug:
        return os.getenv('TG_BOT_TOKEN')
    with DaprClient() as client:
        token = client.get_secret(store_name=store_name, key='TG_BOT_TOKEN').secret['TG_BOT_TOKEN']
    return token


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        service=ServiceConfig(app_id='tg_accessor', pubsub='pubsub', topic='digest_report'),
        bot=BotConfig(
            token=fetch_token(store_name='localsecretstore'),
            max_text_length=4000,
            pause_seconds_between_messages=1
        ),
        grpc_port=50056,
        service_name='tg_accessor'
    )


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
            'filename': 'log/tg_accessor.log',
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
