import worldnewsapi
from worldnewsapi.rest import ApiException
from worldnewsapi.models.search_news200_response import SearchNews200Response
import logging

from config import ParsingConfig
from schema import ParseSettings, Tags


logger = logging.getLogger(__name__)


class NewsUpdater:
    def __init__(self, storage, config: ParsingConfig) -> None:
        self._storage = storage
        self._config = config
        self._api_config = None
        self._init_api(self._config.api_key)

    def _init_api(self, key):
        self._api_config = worldnewsapi.Configuration(
            host='https://api.worldnewsapi.com', ssl_ca_cert=None
        )
        self._api_config.api_key['apiKey'] = key
        self._api_config.api_key['headerApiKey'] = key

    def _request_news(self, params: dict, api_instance) -> SearchNews200Response:
        return api_instance.search_news(**params)

    def _fetch_news_page(self, config, api_instance):
        try:
            response = self._request_news(config, api_instance)
            return response.news if response and response.available > 0 else []
        except ApiException:
            logger.exception('Limit reached, nothing to parse :(')
            return []

    def _fetch_all_news_for_bunch(self, config, api_instance):
        news_list = self._fetch_news_page(config, api_instance)
        if not news_list:
            return []

        available_news = config['number']
        total_pages = available_news // config['number']

        for page in range(1, total_pages + 1):
            config['offset'] = page * config['number']
            logger.info(f'Parsing page {page}/{total_pages}')
            news_page = self._fetch_news_page(config, api_instance)
            if not news_page:
                break
            news_list.extend(news_page)

        return news_list

    def _process_tags_bunch(self, tags_bunch, pub_date):
        config = self._prepare_config(pub_date, tags_bunch)
        with worldnewsapi.ApiClient(self._api_config) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            return self._fetch_all_news_for_bunch(config, api_instance)

    def _collect_news(self, tags_bunches, pub_date):
        all_news = []
        for tags_bunch in tags_bunches:
            news_list = self._process_tags_bunch(tags_bunch, pub_date)
            if news_list:
                all_news.extend(news_list)
            else:
                logger.info(
                    'Stopping further processing due to API limit or empty response.'
                )
                break
        return all_news

    def _save_news(self, news_list):
        if not news_list:
            logger.info('No news collected.')
            return

        logger.info(f'Finished collecting new entries, total {len(news_list)} news collected')
        latest_news_date = max(news.publish_date for news in news_list)
        final_data = [news.model_dump() for news in news_list]

        logger.info('Deleting outdated entries')
        self._storage.delete_old_entries(self._config.news_expiration_hours)
        logger.info('Saving new news and updating latest news time stamp.')
        self._storage.save_news(final_data, latest_news_date)

    def update_news(self, request: Tags):
        tags_list = [tag.strip() for tag in request.tags.split(',')]
        tags_bunches = self._split_tags(tags_list)
        pub_date = self._storage.get_latest_entry_time()
        all_news = self._collect_news(tags_bunches, pub_date)
        self._save_news(all_news)

    def _prepare_config(self, pub_date, bunch) -> dict:
        params = {'text': bunch, 'number': self._config.max_entries}
        config = ParseSettings(**params).dict
        config.update({'earliest_publish_date': pub_date})
        logger.info(f'Config preparation finished: {config}')
        return config

    def _split_tags(self, tags: list[str], max_length=100):
        logger.info('Separating tags to bunches')
        result = []
        current_bunch = ''
        separator = ' OR '
        for tag in tags:
            tag_with_separator = (separator if current_bunch else '') + tag
            if len(current_bunch) + len(tag_with_separator) > max_length:
                result.append(current_bunch)
                current_bunch = tag
            else:
                current_bunch += tag_with_separator
        if current_bunch:
            result.append(current_bunch)
        logger.info(f'Separated tags ready: {result}')
        return result
