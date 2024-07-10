from dataclasses import dataclass


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class GRPCConfig:
    news_accessor_app_id: str
    ai_accessor_app_id: str
    db_accessor_app_id: str
    port: int


@dataclass
class NewsConfig:
    pause_between_updates_minutes: int


@dataclass
class Config:
    logging: LoggingConfig
    grpc: GRPCConfig
    news: NewsConfig


def load_config():
    return Config(
        logging=LoggingConfig(logging_config),
        grpc=GRPCConfig(
            news_accessor_app_id='news_accessor',
            ai_accessor_app_id='ai_accessor',
            db_accessor_app_id='db_accessor',
            port=50051,
        ),
        news=NewsConfig(pause_between_updates_minutes=2),
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
            'filename': 'log/ai_manager.log',
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
