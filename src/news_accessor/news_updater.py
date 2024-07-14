import logging

import worldnewsapi
from worldnewsapi.models.search_news200_response import SearchNews200Response
from worldnewsapi.rest import ApiException

from config import ParsingConfig
from schema import ParseSettings, Tags


logger = logging.getLogger(__name__)


class NewsUpdater:
    """A class that provides an interface to the WorldNews API."""

    def __init__(self, storage, config: ParsingConfig) -> None:
        self._storage = storage
        self._config = config
        self._api_config = None
        self._init_api(self._config.api_key)

    def _init_api(self, key: str) -> None:
        """SDK API initialization."""

        self._api_config = worldnewsapi.Configuration(
            host='https://api.worldnewsapi.com', ssl_ca_cert=None
        )
        self._api_config.api_key['apiKey'] = key
        self._api_config.api_key['headerApiKey'] = key

    def _fetch_news_page(self, config, api_instance):
        """Fetches a single response page, or returns an empty list, even on exception."""

        try:
            response: SearchNews200Response = api_instance.search_news(**config)
            return (response.news, response.available) if response and response.available > 0 else ([], 0)
        except ApiException:
            logger.exception('Limit reached, nothing to parse :(')
        return ([], 0)

    def _fetch_all_news_for_bunch(self, config, api_instance):
        """Fetches all news for a current bunch of tags"""

        news_list, available_news = self._fetch_news_page(config, api_instance)
        if not news_list:
            logger.info('No news in the first page of results, not proceeding.')
            return []

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
        """Given a tags bunch, tries to download all news for it after given time."""

        config = self._prepare_config(pub_date, tags_bunch)
        with worldnewsapi.ApiClient(self._api_config) as api_client:
            api_instance = worldnewsapi.NewsApi(api_client)
            return self._fetch_all_news_for_bunch(config, api_instance)

    def _collect_news(self, tags_bunches, pub_date):
        """The ultimate news collector.
        Collects all pages of news gathered for every tag bunch in tag bunches into a single list."""

        all_news = []
        for tags_bunch in tags_bunches:
            news_list = self._process_tags_bunch(tags_bunch, pub_date)
            if not news_list:
                logger.info(
                    'Stopping further processing due to API limit or empty response.'
                )
                break
            all_news.extend(news_list)
            logger.info(f'News list extender with {len(news_list)} new news')

        return all_news

    def _save_news(self, news_list):
        """Saves the news.
        The interface is provided by the injected Storage class, which currently works with the disk,
        but can be changed to work with a db, cloud, or other storage."""

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
        """The public method to update the news given all users tags."""

        tags_list = [tag.strip() for tag in request.tags.split(',')]
        tags_bunches = self._split_tags(tags_list)
        all_news = self._collect_news(tags_bunches, self._storage.get_latest_entry_time())
        self._save_news(all_news)

    def _prepare_config(self, pub_date, bunch) -> dict:
        """Creates a parsing config for the current tags bunch."""

        params = {'text': bunch, 'number': self._config.max_entries}
        config = ParseSettings(**params).dict
        config.update({'earliest_publish_date': pub_date})
        logger.info(f'Config preparation finished: {config}')
        return config

    def _split_tags(self, tags: list[str]):
        """Splits the tags into bunches.
        So that on every request the query parameters does not exceed configured amount of chars."""

        logger.info('Separating tags to bunches')
        result = []
        current_bunch = ''
        separator = ' OR '
        for tag in tags:
            tag_with_separator = (separator if current_bunch else '') + tag
            if len(current_bunch) + len(tag_with_separator) > self._config.max_query_chars:
                result.append(current_bunch)
                current_bunch = tag
            else:
                current_bunch += tag_with_separator
        if current_bunch:
            result.append(current_bunch)
        logger.info(f'Separated tags ready: {result}')
        return result
