import json
import worldnewsapi
from worldnewsapi.rest import ApiException
from worldnewsapi.models.search_news200_response import SearchNews200Response
import logging

from config import ParsingConfig
from schema import ParseSettings, UpdateNewsRequest


logger = logging.getLogger(__name__)


class NewsUpdater:
    def __init__(self, storage, config: ParsingConfig) -> None:
        self._storage = storage
        self._config = config
        self._api_config = None
        self._init_api(self._config.api_key)

    def _init_api(self, key):
        self._api_config = worldnewsapi.Configuration(host='https://api.worldnewsapi.com', ssl_ca_cert=None)
        self._api_config.api_key['apiKey'] = key
        self._api_config.api_key['headerApiKey'] = key

    def _request_news(self, params: dict, api_instance) -> SearchNews200Response:
        return api_instance.search_news(**params)

    def update_news(self, request: UpdateNewsRequest):
        config = self._parse_request(request.model_dump())
        parse_news_config = config.copy()
        parse_news_config.update({'earliest_publish_date': self._storage.get_latest_entry_time()})
        logger.info(f'Ready to parse with settings: {parse_news_config}')
        with worldnewsapi.ApiClient(self._api_config) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            try:
                response = self._request_news(parse_news_config, api_instance)
            except ApiException:
                logger.exception('Limit reached, nothing to parse :(')
                return
            if not response or response.available == 0:
                logger.info('Empty response received, not proceeding')
                return
            result = response.news
            available, news_in_page = response.available, parse_news_config['number']
            amount_of_pages = available // news_in_page
            logger.info(f'Received response. Total news available {available}')
            if available > news_in_page:
                for page in range(1, amount_of_pages + 1):
                    parse_news_config.update({'offset': page * news_in_page})
                    logger.info(f'Parsing page {page}/{amount_of_pages}')
                    try:
                        result.extend(self._request_news(parse_news_config, api_instance).news)
                    except ApiException as e:
                        logging.exception(f'Error parsing pages: {e}')
                        break
        logger.info(f'Finished collecting new entries, total {len(result)} news collected')
        latest_news = result[0].publish_date
        final_data = [n.model_dump() for n in result]
        logger.info('Deleting outdated entries')
        self._storage.delete_old_entries(self._config.news_expiration_hours)
        logger.info('Saving new news and updating latest news time stamp.')
        self._storage.save_news(final_data, latest_news)

    def _parse_request(self, request: dict) -> ParseSettings:
        logger.info(f'Parsing config for request: {request}')
        result = {
            'text': ' OR '.join([tag.strip() for tag in request['tags'].split(',')]),
            'number': self._config.max_entries
        }
        config = ParseSettings(**result)
        logger.info(f'Parsing finished: {config}')
        return config.dict
