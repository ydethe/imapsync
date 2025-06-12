import imaplib
import os
from pathlib import Path
from typing import List

from .config import config
from . import logger


def connect_to_imap() -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
    mail.login(config.USERNAME, config.PASSWORD)
    return mail


def convert_message(raw_msg: bytes) -> str:
    return raw_msg.decode("utf-8")


def save_eml(uid: str, raw_msg: bytes, folder: Path) -> bool:
    message = convert_message(raw_msg)

    eml_path = folder / f"{uid}.eml"
    if not eml_path.exists():
        with open(eml_path, "w") as f:
            f.write(message)
        return True

    return False


def sync_mailbox(mail: imaplib.IMAP4_SSL, mailbox: str):
    try:
        typ, data = mail.select(mailbox, readonly=True)
    except Exception:
        typ = "NO"
    if typ != "OK":
        logger.warning(f"Failed to select mailbox: {mailbox}")
        return

    typ, data = mail.uid("search", None, "ALL")
    if typ != "OK":
        logger.warning(f"Failed to search mailbox: {mailbox}")
        return

    uids: List[bytes] = data[0].split()
    folder: Path = config.SAVE_DIR / mailbox.replace("/", "_")
    os.makedirs(folder, exist_ok=True)

    for uid in uids:
        uid_str = uid.decode()
        eml_path = os.path.join(folder, f"{uid_str}.eml")
        if os.path.exists(eml_path):
            continue  # Skip already downloaded

        typ, msg_data = mail.uid("fetch", uid, "(RFC822)")
        if typ == "OK":
            raw_msg: bytes = msg_data[0][1]
            save_eml(uid_str, raw_msg, folder)
        else:
            logger.warning(f"Failed to fetch message UID {uid_str}")

        break


def main():
    mail = connect_to_imap()

    sync_mailbox(mail, config.MAILBOX)

    mail.logout()
