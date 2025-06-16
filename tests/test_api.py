import unittest

from imapsync.Email import Email
from imapsync.__main__ import sync_all
from imapsync.imap_sync import connect_to_imap
from imapsync.config import config


class TestIMAPSync(unittest.TestCase):
    def test_main(self):
        sync_all()

    def test_error(self):
        imap_conf = config.IMAP_LIST[1]
        mail = connect_to_imap(imap_conf)

        typ, data = mail.select(imap_conf.MAILBOX, readonly=True)

        uid = b"2298"
        typ, msg_data = mail.uid("fetch", uid, "(RFC822)")
        raw_msg: bytes = msg_data[0][1]
        mail = Email.from_bytes(raw_msg)


if __name__ == "__main__":
    a = TestIMAPSync()

    a.test_main()
    # a.test_error()
