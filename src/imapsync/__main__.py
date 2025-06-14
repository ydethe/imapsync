import schedule

from .imap_sync import sync_all
from .config import config


if __name__ == "__main__":
    schedule.every(config.SYNC_PERIOD).do(sync_all)
