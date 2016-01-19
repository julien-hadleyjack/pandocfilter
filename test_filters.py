import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import minted


class TestMinted(unittest.TestCase):

    def setUp(self):
        self.stdin = sys.stdin

    def tearDown(self):
        sys.stdin.close()
        sys.stdin = self.stdin

    def test(self):
        sys.stdin = open('data/minted_original.json', 'r')

        with tempfile.TemporaryFile("w+") as tmp:
            with redirect_stdout(tmp):
                minted.main()
            tmp.seek(0)
            output = json.loads(tmp.read())

        with open("data/minted_result.json", "r") as result:
            self.assertListEqual(output, json.load(result))


if __name__ == '__main__':
    unittest.main()
