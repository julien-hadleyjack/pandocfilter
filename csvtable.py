#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import csv
import json

import pypandoc

import requests
import sys

from io import StringIO
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
    alignment = paired_attributes.get("align") or paired_attributes.get("aligns") or ""
    if len(alignment) != length:
        alignment = ["default"] * length
    return [ALIGNMENT.get(key.lower(), ALIGNMENT["default"]) for key in alignment]


def convert_to_float(text):
    try:
        return float(text)
    except ValueError:
        return 0.0


def get_widths(length, paired_attributes):
    widths = paired_attributes.get("width") or paired_attributes.get("widths") or ""
    widths = [convert_to_float(width) for width in widths.split(" ")]
    if len(widths) != length:
        widths = [0.0] * length
    return widths


def get_reader(file, paired_attributes):
    return csv.reader(
            file,
            delimiter=paired_attributes.get("paired_attributes", ","),
            quotechar=paired_attributes.get("paired_attributes", '"')
    )


def get_csv_from_url(filename):
    response = requests.get(filename)

    if not response.ok:
        print("CsvTable - Couldn't download: " + filename, file=sys.stderr)
        return

    return StringIO(response.text)


def get_csv(paired_attributes, content):
    filename = paired_attributes.get("url") or paired_attributes.get("file") or ""

    if filename.startswith("http"):
        result = get_csv_from_url(filename)
    elif filename:
        result = open(filename)
    else:
        result = StringIO(content)

    return result


def get_table(args):
    csv_input = get_csv(args["paired_attributes"], args["content"])

    reader = get_reader(csv_input, args["paired_attributes"])
    header = get_header(reader, args["paired_attributes"])
    content = [format_row(row) for row in reader]

    if hasattr(csv_input, "close"):
        csv_input.close()

    alignment = get_alignment(len(content[0]), args["paired_attributes"])
    widths = get_widths(len(content[0]), args["paired_attributes"])

    return Table([], alignment, widths, header, content)


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
