from dataclasses import dataclass
from datetime import timedelta

from dapr.clients import DaprClient


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    db_accessor_app_id: str
    port: int
    pubsub: str
    topic: str


@dataclass
class JWTTokenConfig:
    algorithm: str
    expire_minutes: timedelta
    secret_key: str
    token_type: str


@dataclass
class Config:
    logging: LoggingConfig
    grpc: GRPCConfig
    jwt: JWTTokenConfig
    max_tags: int
    service_name: str


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        grpc=GRPCConfig(db_accessor_app_id='db_accessor', port=50054, pubsub='pubsub', topic='ai_tasks'),
        jwt=configure_token(store_name='localsecretstore'),
        max_tags=3,
        service_name='user_manager'
    )


def configure_token(store_name: str):
    def secret(client, secret_name):
        return client.get_secret(store_name=store_name, key=secret_name).secret[secret_name]
    with DaprClient() as client:
        token_config = JWTTokenConfig(
            algorithm=secret(client, 'JWT_TOKEN_ENCRYPTION_ALGORITHM'),
            secret_key=secret(client, 'JWT_TOKEN_SECRET_KEY'),
            expire_minutes=timedelta(minutes=int(secret(client, 'JWT_TOKEN_EXPIRATION_MINUTES'))),
            token_type=secret(client, 'JWT_TOKEN_TYPE')
        )
    return token_config


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
            'filename': 'log/user_manager.log',
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
