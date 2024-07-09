import worldnewsapi
from worldnewsapi.rest import ApiException
from worldnewsapi.models.search_news200_response import SearchNews200Response
from fake import resp
import logging


logger = logging.getLogger(__name__)







class NewsUpdater:
    def __init__(self, storage, key) -> None:
        self._storage = storage
        self._api_config = None
        self._init_api(key)

    def _init_api(self, key):
        self._api_config = worldnewsapi.Configuration(host='https://api.worldnewsapi.com', ssl_ca_cert=None)
        self._api_config.api_key['apiKey'] = key
        self._api_config.api_key['headerApiKey'] = key

    def _request_news(self, params: dict, api_instance) -> SearchNews200Response:
        try:
            api_response = api_instance.search_news(**params)
        except ApiException:
            logger.warning('The request limit is reached.')
            raise
        except Exception as e:
            logger.error(f'Unexpected exception: {str(e)}')
            raise
        return api_response

    def update_news(self, config: dict):
        parse_news_config = config.copy()
        parse_news_config.update({'earliest_publish_date': self._storage.calculate_latest_entry_time()})
        logger.info(f'Ready to parse with settings: {parse_news_config}')
        result = []
        with worldnewsapi.ApiClient(self._api_config) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            response = self._request_news(parse_news_config, api_instance) or resp()
            if response.available == 0:
                logger.info('Empty response received, not proceeding')
                return
            result.extend(response.news)
            available, news_in_page = response.available, parse_news_config['number']
            logger.info(f'Available news {available=}')
            if available > news_in_page:
                for page in range(1, available // news_in_page + 1):
                    parse_news_config.update({'offset': page * news_in_page})
                    result.extend(self._request_news(parse_news_config, api_instance).news)
        logger.info(f'Finished collecting new entries, total {len(result)} news collected')
        latest_news = result[-1].publish_date
        final_data = [n.dict() for n in result]
        self._storage.save_files(final_data, latest_news)
