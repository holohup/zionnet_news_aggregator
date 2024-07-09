import json
import worldnewsapi
from worldnewsapi.rest import ApiException
from worldnewsapi.models.search_news200_response import SearchNews200Response
import logging

from config import ParsingConfig
from schema import ParseSettings


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
        try:
            api_response = api_instance.search_news(**params)
        except ApiException:
            logger.exception('The request limit is reached.')
            return None
        except Exception as e:
            logger.exception(f'Unexpected exception: {str(e)}')
            return None
        return api_response

    def update_news(self, request: str):
        config = self._parse_request(request)
        parse_news_config = config.copy()
        parse_news_config.update({'earliest_publish_date': self._storage.get_latest_entry_time()})
        logger.info(f'Ready to parse with settings: {parse_news_config}')
        with worldnewsapi.ApiClient(self._api_config) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            response = self._request_news(parse_news_config, api_instance)
            if not response or response.available == 0:
                logger.info('Empty response received, not proceeding')
                return
            result = response.news
            available, news_in_page = response.available, parse_news_config['number']
            logger.info(f'Available news {available=}')
            if available > news_in_page:
                for page in range(1, available // news_in_page + 1):
                    parse_news_config.update({'offset': page * news_in_page})
                    result.extend(self._request_news(parse_news_config, api_instance).news)
        logger.info(f'Finished collecting new entries, total {len(result)} news collected')
        latest_news = result[-1].publish_date
        final_data = [n.model_dump() for n in result]
        logger.info('Deleting outdated entries')
        self._storage.delete_old_entries(self._config.news_expiration_hours)
        logger.info('Saving new news and updating latest news time stamp.')
        self._storage.save_files(final_data, latest_news)

    def _parse_request(self, request: str) -> ParseSettings:
        logger.info(f'Parsing config for request: {request}')
        req_json = json.loads(request)
        result = {
            'text': ' OR '.join([tag.strip() for tag in req_json['tags'].split(',')]),
            'number': self._config.max_entries
        }
        if 'source_countries' in req_json.keys():
            result.update({'source_countries': req_json['source_countries']})
        config = ParseSettings(**result)
        logger.info(f'Parsing finished: {config}')
        return config.dict
