import time
import schedule

from .imap_sync import sync_all
from .config import config
from . import logger


if __name__ == "__main__":
    logger.info(f"{config}")

    sync_all()

    schedule.every(config.SYNC_PERIOD).minutes.do(sync_all)

    while True:
        schedule.run_pending()
        time.sleep(2)
