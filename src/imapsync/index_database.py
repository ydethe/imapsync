from datetime import datetime
import sqlite3

from . import logger
from .config import config


def initialize_state_db():
    """
    Initialize the sqlite database

    """
    index_db_path = config.SAVE_DIR / "sync_index.db"
    config.SAVE_DIR.mkdir(exist_ok=True, parents=True)

    logger.info(f"Using sqlite database '{index_db_path}'")

    conn = sqlite3.connect(index_db_path)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS email_accounts (
            account TEXT PRIMARY KEY,
            last_email REAL
        )
    """
    )
    conn.commit()
    conn.close()


def get_last_sync_date_for_account(account: str) -> datetime:
    """
    Get the stored timestamp for the given path

    Args:
        relpath: Path to a file that has already been processed

    Returns:
        The timestamp of last processing if found. None otherwise

    """
    index_db_path = config.SAVE_DIR / "sync_index.db"
    conn = sqlite3.connect(index_db_path)
    c = conn.cursor()
    c.execute("SELECT last_email FROM email_accounts WHERE account = ?", (account,))
    row = c.fetchone()
    conn.close()
    dt = row[0] if row else None

    if dt is None:
        return None
    else:
        return datetime.fromtimestamp(dt)


def set_last_sync_date_for_account(account: str, dt: datetime):
    """
    Set the stored timestamp for the given path

    Args:
        relpath: Path to a file that has already been processed

    Returns:
        The timestamp of last processing if found. None otherwise

    """
    index_db_path = config.SAVE_DIR / "sync_index.db"
    fdt = dt.timestamp()

    conn = sqlite3.connect(index_db_path)
    c = conn.cursor()
    c.execute("REPLACE INTO email_accounts (account, last_email) VALUES (?, ?)", (account, fdt))
    conn.commit()
    conn.close()
