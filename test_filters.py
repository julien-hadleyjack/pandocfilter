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

    def helper(self, function, input_file, output_file):
        sys.stdin = open(input_file, 'r')

        with tempfile.TemporaryFile("w+") as tmp:
            with redirect_stdout(tmp):
                function()
            tmp.seek(0)
            output = json.loads(tmp.read())

        with open(output_file, "r") as result:
            self.assertListEqual(output, json.load(result))


class TestMinted(BasteTest):

    def test(self):
        self.helper(minted.main, "data/minted_original.json", "data/minted_result.json")


class TestCsvTable(BasteTest):

    def test(self):
        self.helper(csvtable.main, "data/csvtable_original.json", "data/csvtable_result.json")

    def test_pad_element_list(self):
        self.assertListEqual([0, 0, 0, 0], csvtable.pad_element([], 4, 0))
        self.assertListEqual([1, 2, 0, 0], csvtable.pad_element([1, 2], 4, 0))
        self.assertListEqual([1, 2, 3, 4], csvtable.pad_element([1, 2, 3, 4], 4, 0))
        self.assertListEqual([1, 2], csvtable.pad_element([1, 2, 3, 4], 2, 0))

    def test_pad_element_string(self):
        with self.assertRaises(ValueError):
            csvtable.pad_element("", 4, 0)
        self.assertEqual("0000", csvtable.pad_element("", 4, "0"))
        self.assertEqual("1200", csvtable.pad_element("12", 4, "0"))
        self.assertEqual("1234", csvtable.pad_element("1234", 4, "0"))
        self.assertEqual("12", csvtable.pad_element("1234", 2, "0"))


if __name__ == '__main__':
    unittest.main()
