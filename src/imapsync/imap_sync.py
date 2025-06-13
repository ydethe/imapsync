import imaplib
import os
from pathlib import Path
from typing import List

from .config import config, ImapConfiguration
from . import logger
from .Email import eml_to_markdown


def connect_to_imap(cfg: ImapConfiguration) -> imaplib.IMAP4_SSL:
    """Connect to the IMAP server

    Args:
        cfg: Connection information

    Returns:
        A object to interact with the IMAP server

    """
    mail = imaplib.IMAP4_SSL(cfg.IMAP_SERVER, cfg.IMAP_PORT)
    mail.login(cfg.USERNAME, cfg.PASSWORD)
    return mail


def save_eml(uid: str, raw_msg: bytes, folder: Path):
    """Save an email as markdown file locally

    Args:
        uid: Email identifier
        raw_bytes: Raw message retrieved from the IMAP server
        folder: Destination folder of the downloaded emails

    """
    message, status = eml_to_markdown(raw_msg)
    if not status:
        logger.error(f"Conversion error for {uid}")

    eml_path = folder / f"{uid}.md"
    with open(eml_path, "w") as f:
        f.write(message)


def sync_mailbox(mail: imaplib.IMAP4_SSL, mailbox: str):
    """
    Download and process emails

    Args:
        mail: Handler to the IMAP server, got with a call to `connect_to_imap`
        mailbox: Name of the mailbox to download emails from

    """
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


def main():
    for imap_conf in config.IMAP_LIST:
        mail = connect_to_imap(imap_conf)

        sync_mailbox(mail, imap_conf.MAILBOX)

        mail.logout()
