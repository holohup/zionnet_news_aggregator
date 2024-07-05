import os
from dataclasses import dataclass

DEBUG = str(os.getenv('DEBUG', False)).lower() in ('true', 'yes', '1', 'on')


@dataclass
class RedisSettings:
    host: str
    port: int


@dataclass
class StorageSettings:
    email_prefix: str


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    db_accessor_app_id: str


@dataclass
class Config:
    redis: RedisSettings
    logging: LoggingConfig
    storage: StorageSettings
    grpc: GRPCConfig


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        redis=RedisSettings(host='localhost' if DEBUG else 'redis', port=6379),
        storage=StorageSettings(email_prefix='EMAIL:'),
        grpc=GRPCConfig(db_accessor_app_id='db_accessor')
    )


logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '#[%(asctime)s] #%(levelname)-8s %(filename)s:'
            '%(lineno)d - %(name)s - %(message)s'
        }
    },
    'handlers': {
        'default': {'class': 'logging.StreamHandler', 'formatter': 'default', 'level': 'INFO'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'log/db_accessor.log',
            'mode': 'a',
            'level': 'DEBUG',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['default', 'file']
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
