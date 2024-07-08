import os
import re
from dataclasses import dataclass
from dapr.clients import DaprClient


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
class AdminsConfig:
    admin_emails: list[str]


@dataclass
class GRPCSettings:
    port: int


@dataclass
class Config:
    redis: RedisSettings
    logging: LoggingConfig
    storage: StorageSettings
    grpc: GRPCSettings
    admins: AdminsConfig


def get_admins(store_name: str):
    with DaprClient() as client:
        key = 'ADMIN_EMAILS'
        admins_str = client.get_secret(store_name=store_name, key=key).secret[key]
    result = admins_str.split(',')
    valid_emails = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    for admin_email in result:
        if not re.fullmatch(valid_emails, admin_email):
            raise ValueError(f'Not a valid admin e-mail: {admin_email}')
    return result


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        redis=RedisSettings(host='localhost' if DEBUG else 'redis', port=6379),
        storage=StorageSettings(email_prefix='EMAIL:'),
        grpc=GRPCSettings(port=50052 if DEBUG else 50051),
        admins=AdminsConfig(admin_emails=get_admins('localsecretstore'))
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
