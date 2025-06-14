import schedule

from .imap_sync import sync_all


if __name__ == "__main__":
    schedule.every().minute.do(sync_all)
