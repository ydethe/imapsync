import imaplib
import os

from .config import config


def connect_to_imap():
    mail = imaplib.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
    mail.login(config.USERNAME, config.PASSWORD)
    return mail


def save_eml(uid, raw_msg, folder):
    eml_path = os.path.join(folder, f"{uid}.eml")
    if not os.path.exists(eml_path):
        with open(eml_path, "wb") as f:
            f.write(raw_msg)
        return True
    return False


def sync_mailbox(mail, mailbox):
    print(f"Syncing mailbox: {mailbox}")
    mail.select(mailbox, readonly=True)
    typ, data = mail.uid("search", None, "ALL")
    if typ != "OK":
        print(f"Failed to search mailbox: {mailbox}")
        return

    uids = data[0].split()
    folder = os.path.join(config.SAVE_DIR, mailbox.replace("/", "_"))
    os.makedirs(folder, exist_ok=True)

    for uid in uids:
        uid_str = uid.decode()
        eml_path = os.path.join(folder, f"{uid_str}.eml")
        if os.path.exists(eml_path):
            continue  # Skip already downloaded

        typ, msg_data = mail.uid("fetch", uid, "(RFC822)")
        if typ == "OK":
            raw_msg = msg_data[0][1]
            save_eml(uid_str, raw_msg, folder)
        else:
            print(f"Failed to fetch message UID {uid_str}")


def main():
    mail = connect_to_imap()
    typ, mailboxes = mail.list()
    if typ != "OK":
        print("Failed to list mailboxes.")
        return

    for mbox in mailboxes:
        parts = mbox.decode().split(' "/" ')
        if len(parts) == 2:
            mailbox = parts[1].strip('"')
            sync_mailbox(mail, mailbox)

    mail.logout()
