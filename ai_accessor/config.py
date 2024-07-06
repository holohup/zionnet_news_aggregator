from dataclasses import dataclass
from dapr.clients import DaprClient
import os


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    user_manager_app_id: str


@dataclass
class SecretsConfig:
    store_name: str


@dataclass
class Config:
    logging: LoggingConfig
    grpc: GRPCConfig
    secrets: SecretsConfig


def configure_env_variables(store_name: str):
    with DaprClient() as client:
        for var in ('GLOBAL_LLM_SERVICE', 'OPENAI_API_KEY', 'OPENAI_ORG_ID'):
            os.environ[var] = client.get_secret(store_name=store_name, key=var).secret[var]


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        grpc=GRPCConfig(user_manager_app_id='user_manager'),
        secrets=SecretsConfig(store_name='localsecretstore')
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
