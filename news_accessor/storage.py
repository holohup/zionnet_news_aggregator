from abc import ABC, abstractmethod
import logging
import json
from datetime import datetime, timedelta, UTC
import os
from config import FilenamesConfig

logger = logging.getLogger(__name__)


class Storage(ABC):
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

    def delete_old_entries(self, news_expiration_hours: timedelta):
        logger.info('Deleting old entries')
        cut_off_date_utc = datetime.now(UTC) - news_expiration_hours
        cut_off_date = cut_off_date_utc.replace(tzinfo=None)
        logger.info(f'Purging news from {cut_off_date}')
        old_news = self._read_news_file()
        self._save_filtered_entries(self._filter_entries(cut_off_date, old_news))

    def _read_news_file(self):
        if not os.path.exists(self._config.news_filename):
            with open(self._config.news_filename, 'w') as file:
                json.dump([], file)
            return []
        with open(self._config.news_filename, 'r') as file:
            data = json.load(file)
        return data

    def _filter_entries(self, cut_off_date: datetime, news: list) -> list:
        return [n for n in news if self._dt_from_pd(n['publish_date']) > cut_off_date]

    def _save_filtered_entries(self, filtered_entries):
        with open(self._config.news_filename, 'w') as file:
            json.dump(filtered_entries, file, indent=4, default=str)
            file.write('\n')

    def save_news(self, final_data, latest_news_date):
        logger.info(f'Saving news files. {len(final_data)=}, {latest_news_date=}')
        if not final_data:
            logger.info('No new news, not messing with files')
            return
        try:
            news = self._read_news_file()
        except json.decoder.JSONDecodeError:
            news = []
        else:
            news.extend(final_data)
            news_after_last = self._filter_entries(self.get_latest_entry_time(format='datetime'), news)
            sorted_news = sorted(
                news_after_last, key=lambda x: self._dt_from_pd(x['publish_date'])
            )
            with open(self._config.news_filename, 'w') as file:
                json.dump(sorted_news, file, indent=4, default=str)
                file.write('\n')
        with open(self._config.latest_update_filename, 'w') as file:
            json.dump({'latest_entry': latest_news_date}, file, default=str)
        logger.info('Files saved')

    def get_latest_entry_time(self, format: str = ''):
        if not os.path.exists(self._config.latest_update_filename):
            publish_date = self._get_dt_from_the_past(24)
        else:
            with open(self._config.latest_update_filename, 'r') as file:
                result = json.load(file)
            publish_date = self._dt_from_pd(result['latest_entry'])
        new_publish_date = publish_date + timedelta(seconds=1)
        if format == 'datetime':
            return new_publish_date
        return new_publish_date.strftime("%Y-%m-%d %H:%M:%S")

    def _get_dt_from_the_past(self, hours_before):
        offset = datetime.now(UTC) - timedelta(hours=hours_before)
        return offset.replace(tzinfo=None)

    def get_all_news_after_strtime(self, strtime: str):
        if not strtime:
            dt = self._get_dt_from_the_past(24)
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
        return datetime.strptime(pd, "%Y-%m-%d %H:%M:%S")
