import unittest

from imapsync.__main__ import sync_all


class TestIMAPSync(unittest.TestCase):
    def test_main(self):
        sync_all()


if __name__ == "__main__":
    a = TestIMAPSync()

    a.test_main()
