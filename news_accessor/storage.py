import logging
import json
from datetime import datetime, timedelta
from config import FilenamesConfig

logger = logging.getLogger(__name__)


class FileStorage:
    def __init__(self, filename_config: FilenamesConfig):
        self._config = filename_config

    def delete_old_entries(self, cut_off_date: datetime):
        logger.info('Deleting old entries')
        self._save_filtered_entries(self._filter_entries(cut_off_date))

    def _read_news_file(self):
        with open(self._config.news_filename, 'r') as file:
            data = json.load(file)
        return data

    def _filter_entries(self, cut_off_date):
        news = self._read_news_file()
        filtered_news = [n for n in news if datetime.strptime(n['publish_date'], '%Y-%m-%d %H:%M:%S') > cut_off_date]
        return filtered_news

    def _save_filtered_entries(self, filtered_entries):
        with open(self._config.news_filename, 'w') as file:
            json.dump(filtered_entries, file)
            file.write('\n')

    def save_files(self, final_data, latest_news):
        logger.info(f'Saving news files. {len(final_data)=}, {latest_news=}')
        if not final_data:
            logger.info('No new news, not messing with files')
            return
        try:
            news = self._read_news_file()
        except json.decoder.JSONDecodeError:
            news = []
        else:
            news.extend(final_data)
            with open(self._config.news_filename, 'w') as file:
                json.dump(news, file, indent=4, default=str)
                file.write('\n')
        with open(self._config.latest_update_filename, 'w') as file:
            json.dump({'latest_entry': latest_news}, file, default=str)
        logger.info('Files saved')

    def calculate_latest_entry_time(self):
        with open(self._config.latest_update_filename, 'r') as file:
            result = json.load(file)
        publish_date = datetime.strptime(result['latest_entry'], "%Y-%m-%d %H:%M:%S")
        new_publish_date = publish_date + timedelta(seconds=1)
        return new_publish_date.strftime("%Y-%m-%d %H:%M:%S")
