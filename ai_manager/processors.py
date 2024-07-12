import logging
from config import ServiceConfig
from schema import (
    CreateDigestAIResponse,
    CreateDigestRequest,
    NewNewsResponse,
    ReporterRequest,
    UserResponse,
)
from db_accessor import DB_Accessor
from ai_accessor import AI_Accessor
from news_accessor import News_Accessor
from id_accountant import IDAccountant
from invokers import publish_message_sync


logger = logging.getLogger(__name__)


class MessageProcessor:
    def __init__(
        self, ai: AI_Accessor, db: DB_Accessor, news: News_Accessor, id_acc: IDAccountant, report_config: ServiceConfig
    ) -> None:
        self._ai = ai
        self._db = db
        self._news = news
        self._request_attributes = id_acc
        self._reporter = report_config

    def process_create_digest_request(self, message: CreateDigestRequest):
        logger.warning(f'Creating digest for {message.email}')
        user: UserResponse = self._db.get_user(message.email)
        if not user:
            logger.error('Could not get user, aborting')
            return
        logger.info('User fetched, proceeding with digest creation')
        all_new_news: NewNewsResponse = self._news.get_new_news(
            user.latest_news_processed
        )
        logger.info('Fetched all new news. Generating digest.')
        result = self._ai.create_digest(
            user,
            all_new_news,
            self._request_attributes.new_id(
                contact=user.contact_info, latest_update=all_new_news.last_news_time, email=message.email
            )
        )
        if not result:
            logger.info('Request sent to queue')
            return
        logger.error(f'Something went wrong. {result}')

    def process_digest_result(self, message: CreateDigestAIResponse):
        logger.info('Received digest generation result.')
        details = self._request_attributes[message.id]
        if not details:
            return
        request = ReporterRequest(contact=details.contact_info, digest=message.digest)
        logger.info('Publishing to reporter queue.')
        result = publish_message_sync(
            pubsub_name=self._reporter.pubsub, topic_name=self._reporter.topic, data=request.model_dump()
        )
        if result:
            logger.error(f'Could not publish message: {result}')
            return
        logger.info('Published sucessfully. Updating users last news update time.')
        update_result = self._db.update_last_news_time(email=details.email, latest_update_time=details.latest_update)
        if update_result:
            logger.error(f'Could not update user latest news processed time: {update_result}')
            return
        logger.info('Updated. Digest processing complete')
