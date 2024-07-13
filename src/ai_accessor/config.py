import os
from dataclasses import dataclass

from dapr.clients import DaprClient

DEBUG = str(os.getenv('DEBUG', False)).lower() in ('true', '1', 'yes', 'debug')


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    topic: str
    port: int
    pubsub: str


@dataclass
class SecretsConfig:
    store_name: str


@dataclass
class AIConfig:
    model_id: str


@dataclass
class Config:
    logging: LoggingConfig
    grpc: GRPCConfig
    secrets: SecretsConfig
    ai: AIConfig


def configure_env_variables(store_name: str):
    with DaprClient() as client:
        for var in ('GLOBAL_LLM_SERVICE', 'OPENAI_API_KEY', 'OPENAI_ORG_ID'):
            os.environ[var] = client.get_secret(store_name=store_name, key=var).secret[var]


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        grpc=GRPCConfig(topic='ai_tasks', port=50053, pubsub='pubsub'),
        secrets=SecretsConfig(store_name='localsecretstore'),
        ai=AIConfig(model_id='gpt-3.5-turbo')
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
            'filename': 'log/ai_accessor.log',
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
