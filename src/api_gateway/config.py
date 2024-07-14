from dataclasses import dataclass

from dapr.clients import DaprClient


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    user_manager_app_id: str
    news_aggregation_manager_pubsub: str
    news_aggregation_manager_topic: str


@dataclass
class JTWConfig:
    algorithm: str
    secret_key: str
    token_type: str


@dataclass
class Config:
    logging: LoggingConfig
    grpc: GRPCConfig
    jwt: JTWConfig
    service_name: str


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        grpc=GRPCConfig(
            user_manager_app_id='user_manager',
            news_aggregation_manager_pubsub='pubsub',
            news_aggregation_manager_topic='ai_tasks'
        ),
        jwt=configure_token(store_name='localsecretstore'),
        service_name='api_gateway'
    )


def configure_token(store_name: str):
    def secret(client, secret_name):
        return client.get_secret(store_name=store_name, key=secret_name).secret[secret_name]
    with DaprClient() as client:
        token_config = JTWConfig(
            algorithm=secret(client, 'JWT_TOKEN_ENCRYPTION_ALGORITHM'),
            secret_key=secret(client, 'JWT_TOKEN_SECRET_KEY'),
            token_type=secret(client, 'JWT_TOKEN_TYPE')
        )
    return token_config


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
        'default': {'class': 'logging.StreamHandler', 'formatter': 'default', 'level': 'INFO'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'log/api_gateway.log',
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
