#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import csvtable
import minted


class BasteTest(unittest.TestCase):

    def setUp(self):
        self.stdin = sys.stdin

    def tearDown(self):
        sys.stdin.close()
        sys.stdin = self.stdin


class TestMinted(BasteTest):

    def test(self):
        sys.stdin = open('data/minted_original.json', 'r')

        with tempfile.TemporaryFile("w+") as tmp:
            with redirect_stdout(tmp):
                minted.main()
            tmp.seek(0)
            output = json.loads(tmp.read())

        with open("data/minted_result.json", "r") as result:
            self.assertListEqual(output, json.load(result))


class TestCsvTable(BasteTest):

    def test(self):
        sys.stdin = open('data/csvtable_original.json', 'r')

        with tempfile.TemporaryFile("w+") as tmp:
            with redirect_stdout(tmp):
                csvtable.main()
            tmp.seek(0)
            output = json.loads(tmp.read())

        with open("data/csvtable_result.json", "r") as result:
            self.assertListEqual(output, json.load(result))


if __name__ == '__main__':
    unittest.main()
