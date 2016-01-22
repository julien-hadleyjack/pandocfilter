#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import csv
import json
import tempfile

import pypandoc

import requests
from pandocfilters import Table, elt, toJSONFilter, Plain

# Missing constructors for Pandoc elements
ALIGNMENT = {
    "l": elt("AlignLeft", 1)([]),
    "c": elt("AlignCenter", 1)([]),
    "r": elt("AlignRight", 1)([]),
    "default": elt("AlignDefault", 1)([]),
}


def map_attributes(attributes):
    return {key: value for key, value in attributes}


def check_preconditions(key, value, meta, **kwargs):
    return key == "CodeBlock" and "table" in value[0][1]


def markdown_to_json(content):
    return json.loads(pypandoc.convert(content, format='md', to="json"))[1][0]


def para_to_plain(elem):
    return Plain(elem["c"])


def format_row(row):
    return [[para_to_plain(markdown_to_json(elem))] for elem in row]


def get_header(reader, paired_attributes):
    if paired_attributes.get("header"):
        return format_row(next(reader))
    else:
        return []


def get_alignment(length, paired_attributes):
    alignment = paired_attributes.get("align", "")
    if len(alignment) != length:
        alignment = " " * length
    return [ALIGNMENT.get(key.lower(), ALIGNMENT["default"]) for key in alignment]


def get_reader(file, paired_attributes):
    return csv.reader(
            file,
            delimiter=paired_attributes.get("paired_attributes", ","),
            quotechar=paired_attributes.get("paired_attributes", '"')
    )


def get_csv_from_url(paired_attributes):
    filename = paired_attributes.get("file", "")

    if not filename.startswith("http"):
        return

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        response = requests.get(filename, stream=True)

        if not response.ok:
            return

        for block in response.iter_content(1024):
            tmp_file.write(block)

        paired_attributes["file"] = tmp_file.name


def get_table(args):
    get_csv_from_url(args["paired_attributes"])

    with open(args["paired_attributes"]["file"]) as file:
        reader = get_reader(file, args["paired_attributes"])
        header = get_header(reader, args["paired_attributes"])
        content = [format_row(row) for row in reader]

    alignment = get_alignment(len(content[0]), args["paired_attributes"])

    return Table([], alignment, [0, 0], header, content)


def csv_table(key, value, fmt, meta):
    if not check_preconditions(**locals()):
        return

    (_, classes, paired_attributes), content = value

    paired_attributes = map_attributes(paired_attributes)

    return get_table(locals())


def main():
    toJSONFilter(csv_table)


if __name__ == '__main__':
    main()
