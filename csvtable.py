#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json

import pypandoc
from pandocfilters import Table, elt, toJSONFilter

AlignDefault = elt("AlignDefault", 1)


def map_attributes(attributes):
    return {key: value for key, value in attributes}


def check_preconditions(key, value, meta, **kwargs):
    return key == "CodeBlock" and "table" in value[0][1]


def markdown_to_json(content):
    return json.loads(pypandoc.convert(content, format='md', to="json"))[1][0]


def para_to_plain(elem):
    elem["t"] = "Plain"
    return elem


def get_table(filename):
    header = []
    content = []
    with open(filename) as file:
        reader = csv.reader(file)
        for row in reader:
            if not header:
                header.extend([[para_to_plain(markdown_to_json(elem))] for elem in row])
            else:
                content.append([[para_to_plain(markdown_to_json(elem))] for elem in row])

    return Table([], [AlignDefault([]), AlignDefault([])], [0, 0], header, content)


def csv_table(key, value, fmt, meta):
    if not check_preconditions(**locals()):
        return

    (_, classes, paired_attributes), content = value

    paired_attributes = map_attributes(paired_attributes)

    return get_table(paired_attributes["file"])


def main():
    toJSONFilter(csv_table)


if __name__ == '__main__':
    main()
