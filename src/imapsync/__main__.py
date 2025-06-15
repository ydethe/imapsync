import time
import schedule

from .imap_sync import sync_all
from .config import config


if __name__ == "__main__":
    schedule.every(config.SYNC_PERIOD).minutes.do(sync_all)

    while True:
        schedule.run_pending()
        time.sleep(2)
