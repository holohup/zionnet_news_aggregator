from dataclasses import dataclass


@dataclass
class LoggingConfig:
    settings: dict


@dataclass
class ServiceConfig:
    pubsub: str
    topic: str
    app_id: str

@dataclass
class GRPCConfig:
    news: ServiceConfig
    ai: ServiceConfig
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
            news=ServiceConfig(app_id='news_accessor', pubsub='pubsub', topic='news_tasks'),
            ai=ServiceConfig(app_id='ai_accessor', pubsub='pubsub', topic='ai_tasks'),
            db_accessor_app_id='db_accessor',
            port=50055,
        ),
        news=NewsConfig(pause_between_updates_minutes=60),
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
