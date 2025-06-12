import unittest


from imapsync.__main__ import main


class TestIMAPSync(unittest.TestCase):
    def test_main(self):
        main()


if __name__ == "__main__":
    a = TestIMAPSync()

    a.test_main()
