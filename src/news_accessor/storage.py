import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import UTC, datetime, timedelta

from config import FilenamesConfig

logger = logging.getLogger(__name__)


class Storage(ABC):
    """And abstract class, its child will be injected into a news updater class.
    It will take care of storage - related operations."""

    @abstractmethod
    def delete_old_entries(self, news_expiration_hours: timedelta):
        pass

    @abstractmethod
    def save_news(self, final_data, latest_news_date):
        pass

    @abstractmethod
    def get_latest_entry_time(self, format: str = ''):
        pass

    @abstractmethod
    def get_all_news_after_strtime(self, dt: datetime):
        pass


class FileStorage(Storage):
    def __init__(self, filename_config: FilenamesConfig):
        self._config = filename_config

    def delete_old_entries(self, news_expiration_hours: timedelta) -> None:
        """Deletes the outdated entries given expiration hours and knowing current time."""

        logger.info('Deleting old entries')
        cut_off_date_utc = datetime.now(UTC) - news_expiration_hours
        cut_off_date = cut_off_date_utc.replace(tzinfo=None)
        logger.info(f'Purging news from {cut_off_date}')
        old_news = self._read_news_file()
        filtered_entries = self._filter_entries(cut_off_date, old_news)
        self._save_filtered_entries(filtered_entries)
        logger.info(f'Purged {len(old_news) - len(filtered_entries)} old news')

    def _read_news_file(self) -> list[dict]:
        """Reads the news file from the disk."""

        if not os.path.exists(self._config.news_filename):
            with open(self._config.news_filename, 'w') as file:
                json.dump([], file)
            return []
        with open(self._config.news_filename, 'r') as file:
            data = json.load(file)
        return data

    def _filter_entries(self, cut_off_date: datetime, news: list) -> list:
        """Filters out the outdated entries given the cutoff date."""

        return [n for n in news if self._dt_from_pd(n['publish_date']) > cut_off_date]

    def _save_filtered_entries(self, filtered_entries) -> None:
        """Saves the filtered entries to disk in an indented JSON."""

        with open(self._config.news_filename, 'w') as file:
            json.dump(filtered_entries, file, indent=4, default=str)
            file.write('\n')

    def save_news(self, final_data, latest_news_date) -> None:
        """The public function to save the news. """

        logger.info(f'Saving news files. {len(final_data)} new entries, {latest_news_date=}')
        if not final_data:
            logger.info('No new news, not messing with files')
            return
        try:
            news = self._read_news_file()
        except json.decoder.JSONDecodeError:
            news = []
        else:
            news.extend(final_data)
            unique_news = self._filter_unique_by_id(news)
            sorted_news = sorted(unique_news, key=lambda x: self._dt_from_pd(x['publish_date']))
            with open(self._config.news_filename, 'w') as file:
                json.dump(sorted_news, file, indent=4, default=str)
                file.write('\n')
        with open(self._config.latest_update_filename, 'w') as file:
            json.dump({'latest_entry': latest_news_date}, file, default=str)
        logger.info('Files saved')

    def get_latest_entry_time(self, format: str = '') -> datetime | str:
        """Returns the latest news update time in either datetime or str."""

        if not os.path.exists(self._config.latest_update_filename):
            publish_date = self._get_dt_from_the_past(
                self._config.latest_update_time_from_now_if_no_file_exists
            )
        else:
            with open(self._config.latest_update_filename, 'r') as file:
                result = json.load(file)
            publish_date = self._dt_from_pd(result['latest_entry'])
        new_publish_date = publish_date + timedelta(
            seconds=self._config.time_delta_seconds_to_avoid_collisions
        )
        if format == 'datetime':
            return new_publish_date
        return new_publish_date.strftime("%Y-%m-%d %H:%M:%S")

    def _filter_unique_by_id(self, news_list: list) -> list:
        """Filters the news by unique id."""

        seen_ids = set()
        return [
            news for news in news_list if news['id'] not in seen_ids and not seen_ids.add(news["id"])
        ]

    def _get_dt_from_the_past(self, hours_before) -> datetime:
        """Returns datetime from the past to the current time in UTC"""

        offset = datetime.now(UTC) - timedelta(hours=hours_before)
        return offset.replace(tzinfo=None)

    def get_all_news_after_strtime(self, strtime: str):
        """Public method to get all new news from a specific time in str."""

        if not strtime:
            dt = self._get_dt_from_the_past(24 * 7)
        else:
            dt = self._dt_from_pd(strtime)
        logger.info(f'Fetching all news from {dt}')
        data = self._read_news_file()
        found_first_entry = False
        i = 0
        while not found_first_entry and i < len(data):
            if self._dt_from_pd(data[i]['publish_date']) <= dt:
                i += 1
                continue
            found_first_entry = True
        logger.info(f'Returning {len(data) - i} out of {len(data)} entries.')
        return data[i:]

    def _dt_from_pd(self, pd: str) -> datetime:
        """Converts time from a string as stored in publish_date to datetime."""

        return datetime.strptime(pd, "%Y-%m-%d %H:%M:%S")
