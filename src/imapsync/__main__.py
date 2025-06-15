import time
import schedule

from .imap_sync import sync_all
from .config import config
from . import logger


if __name__ == "__main__":
    schedule.every(config.SYNC_PERIOD).minutes.do(sync_all)
    logger.info("Started imapsync")

    while True:
        schedule.run_pending()
        time.sleep(2)
