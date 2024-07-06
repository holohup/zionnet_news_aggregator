from dataclasses import dataclass


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    db_accessor_app_id: str


@dataclass
class Config:
    logging: LoggingConfig
    grpc: GRPCConfig


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        grpc=GRPCConfig(db_accessor_app_id='db_accessor')
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
