import imaplib
from pathlib import Path
from typing import List

from tqdm import tqdm

from .config import config, ImapConfiguration
from . import logger
from .Email import Email


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


def save_eml(uid: str, raw_msg: bytes, folder: Path) -> Email:
    """Save an email as markdown file locally

    Args:
        uid: Email identifier
        raw_bytes: Raw message retrieved from the IMAP server
        folder: Destination folder of the downloaded emails

    Returns:
        Date of the email

    """
    try:
        mail = Email.from_bytes(raw_msg)
        parsing_status = mail.parsing_status
    except Exception:
        mail = None
        parsing_status = False

    if parsing_status:
        eml_path = folder / f"{uid}.md"
        mail.save_to_file(eml_path)
    else:
        bin_path = folder / f"{uid}.bin"
        logger.error(f"Conversion error for {uid}. Dumping to {bin_path}")
        with open(bin_path, "wb") as f:
            f.write(raw_msg)

    return mail


def sync_mailbox(mail: imaplib.IMAP4_SSL, label: str, mailbox: str):
    """
    Download and process emails

    Args:
        mail: Handler to the IMAP server, got with a call to `connect_to_imap`
        mailbox: Name of the mailbox to download emails from

    """
    logger.info(f"Syncing: {label}")

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
    folder: Path = config.SAVE_DIR / label
    folder.mkdir(parents=True, exist_ok=True)

    for uid in tqdm(uids):
        uid_str = uid.decode()
        eml_path = folder / f"{uid_str}.md"
        if eml_path.exists():
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

        sync_mailbox(mail, imap_conf.LABEL, imap_conf.MAILBOX)

        mail.logout()
