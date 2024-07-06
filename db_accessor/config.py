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
class GRPCSettings:
    port: int


@dataclass
class Config:
    redis: RedisSettings
    logging: LoggingConfig
    storage: StorageSettings
    grpc: GRPCSettings


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        redis=RedisSettings(host='localhost' if DEBUG else 'redis', port=6379),
        storage=StorageSettings(email_prefix='EMAIL:'),
        grpc=GRPCSettings(port=50052 if DEBUG else 50051)
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
