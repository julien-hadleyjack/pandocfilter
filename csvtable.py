#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Include content from CSV files as tables in Pandoc.

It is based on:
https://github.com/mb21/pandoc-placetable
https://github.com/baig/pandoc-csv2table
"""

from __future__ import print_function

import argparse
import csv
import json

import pypandoc

import requests
import sys

from io import StringIO
from pandocfilters import Table, elt, toJSONFilter, Plain

# Missing constructors for Pandoc elements responsible for the column alignment in tables
ALIGNMENT = {
    "l": elt("AlignLeft", 1)([]),
    "c": elt("AlignCenter", 1)([]),
    "r": elt("AlignRight", 1)([]),
    "d": elt("AlignDefault", 1)([]),
}


def map_attributes(attributes):
    """
    By default pandoc will return a list of string for the paired attributes.
    This function will create a dictionary with the elements of the list.

    :param attributes: A list of in the order of: key1, value1, key2, value2,...
    :type attributes: list[str]
    :return: The dictionary of the paired attributes
    :rtype: dict[str, str]
    """
    return {key: value for key, value in attributes}


def check_preconditions(key, value):
    """
    Check if the filter applies to the current element in the syntax tree.

    :param key: The type of pandoc object.
    :type key: str
    :param value: The contents of the object.
    :type value: list | str
    :return: ``True`` if the filter applices to the current element, ``False`` otherwise.
    :rtype: bool
    """
    return key == "CodeBlock" and "table" in value[0][1]


def format_cell(content):
    """
    Interpret the cell content as markdown and convert it to the JSON structure used by pandoc.
    This function uses `pypandoc <https://pypi.python.org/pypi/pypandoc/>`_ for the conversion.

    :param content: The cell content which can contain markdown formatting
    :type content: str
    :return: Returns either an empty list (if content is empty) or with one "Plain" element with the JSON as content
    :rtype: list
    """
    result = json.loads(pypandoc.convert(content, format='md', to="json"))
    return [Plain(result[1][0]["c"])] if result[1] else []


def get_row(row):
    """
    Returns the content of the row already formatted.

    :param row: The list of the row with the cell content as string elements
    :type row: list[str]
    :return: A list of the row with the cell content as elements used by pandoc
    :rtype: list[list]
    """
    return [format_cell(elem) for elem in row]


def get_header(reader, paired_attributes):
    """
    Returns the content of the header already formatted if a header exists.

    :param reader: The csv reader
    :type reader: csv.reader
    :param paired_attributes: The paired attributes for the code
    :type paired_attributes: dict[str, str]
    :return: A list of the header row with the cell content as elements used by pandoc or an empty list if no header
    :rtype: list
    """
    return get_row(next(reader)) if get_setting("header", False, paired_attributes) else []


def get_alignment(column_number, paired_attributes):
    """
    Returns usable alignment settings for the table columns.
    The alignment can be: L (left), C (center), R (right) or d (default).
    Pads the provided values if they don't exist or not of the required length with the default value.

    :param column_number: The number of columns of the table.
    :type column_number: int
    :param paired_attributes: The paired attributes for the code contain either "align" or "aligns" with the alignments
    :type paired_attributes: dict[str, str]
    :return: The list with alignments
    :rtype: list
    """
    alignment = list(get_setting(["align", "aligns"], "", paired_attributes))
    alignment = pad_element(alignment, column_number, "d")
    return [ALIGNMENT.get(key.lower(), ALIGNMENT["d"]) for key in alignment]


def convert_to_float(text, default=0.0):
    """
    Converts a string to a float. If the string can't be converted to a string, return the default.

    :param text: The string to be converted to a float (e.g. "0.4")
    :type text: str
    :param default: The default value
    :type default: float
    :return: The resulting float
    :rtype: float
    """
    try:
        return float(text)
    except ValueError:
        return default


def pad_element(element, wanted_length, pad_value):
    """
    Pads the element with the pad_value so that it the length is equal to wanted_length.
    If element is longer than the wanted_length, then the element will cut to that length.

    :param element: The element that should be padded.
    :type element: str | list
    :param wanted_length: The length that the element should be.
    :type wanted_length: int
    :param pad_value: The value that is used for padding the element.
    :return: The element
    :raises ValueError: If the element is string but the pad_value is not.
    """
    if isinstance(element, str) and not isinstance(pad_value, str):
        raise ValueError("Value needs to be string to concatenate to string element (not {}).".format(type(pad_value)))
    if len(element) < wanted_length:
        if isinstance(element, list):
            element += [pad_value] * (wanted_length - len(element))
        else:
            element += pad_value * (wanted_length - len(element))
    else:
        element = element[:wanted_length]
    return element


def get_widths(column_number, paired_attributes):
    """
    Returns width values for the table columns.
    Pads the provided values if they don't exist or are missing for some columnwith the default value.

    :param column_number: The number of columns of the table.
    :type column_number: int
    :param paired_attributes: The paired attributes for the code containing either "width" or "widths" with the widths.
    :type paired_attributes: dict[str, str]
    :return: The list with the widths
    :rtype: list
    """
    widths = get_setting(["width", "widths"], "", paired_attributes)
    widths = [convert_to_float(width) for width in widths.split(" ")]
    widths = pad_element(widths, column_number, 0.0)
    return widths


def get_reader(file, paired_attributes):
    """
    Returns the CSV reader for a file.

    :param file: The file for the CSV content.
    :type file: io.StringIO
    :param paired_attributes: The paired attributes for the code which can contain "delimiter" and "quotechar" settings.
    :return: The CSV reader
    :rtype: csv.reader
    """
    return csv.reader(
            file,
            delimiter=get_setting("delimiter", ",", paired_attributes),
            quotechar=get_setting("quotechar", '"', paired_attributes)
    )


def get_content_from_url(url):
    """
    Get content from an url. This method can be used to download a CSV file.

    :param url: The url where the content should be loaded from.
    :type url: str
    :return: The content at the url.
    :rtype: io.StringIO
    """
    response = requests.get(url)

    if not response.ok:
        print("CsvTable - Couldn't download: " + url, file=sys.stderr)
        return

    return StringIO(response.text)


def get_csv(paired_attributes, content):
    """
    Return the CSV content. This method will look at urls, files and code block content.

    :param paired_attributes:
    :type paired_attributes: dict[str, str]
    :param content: The code block content
    :return: The CSV content.
    :rtype: io.StringIO
    """
    filename = get_setting(["url", "file"], "", paired_attributes)

    if filename.startswith("http"):
        result = get_content_from_url(filename)
    elif filename:
        result = open(filename)
    else:
        result = StringIO(content)

    return result


def get_setting(key, default_value="", paired_attributes=None, meta=None, remove=False):
    """
    Looks at the attributes of the code and the metadata of the document (in that order) and returns the value when it
    finds one with the specified key.

    :param key: The key or keys that should be searched for. Only the result for the first key found will be returned.
    :type key: str | list[str]
    :param default_value: The value that should be found if the key(s) can't be found.
    :type default_value: str | object
    :param paired_attributes:
    :type paired_attributes: dict[str, str]
    :param meta: The metadata of the document.
    :type meta: dict[str, str]
    :param remove: Should the setting be removed from the attributes if it was found there.
    :type remove: bool
    :return: The value that is associated with the key or the default value if key not found.
    :rtype: str | object
    """
    if not isinstance(key, list):
        key = [key]
    for single_key in key:
        if single_key in paired_attributes:
            return paired_attributes.pop(single_key) if remove else paired_attributes[single_key]
        if meta is not None and single_key in meta:
            return meta[single_key]
    return default_value


def get_table(paired_attributes, content):
    csv_input = get_csv(paired_attributes, content)

    reader = get_reader(csv_input, paired_attributes)
    header = get_header(reader, paired_attributes)
    csv_content = [get_row(row) for row in reader]

    if hasattr(csv_input, "close"):
        csv_input.close()

    alignment = get_alignment(len(csv_content[0]), paired_attributes)
    widths = get_widths(len(csv_content[0]), paired_attributes)

    return Table([], alignment, widths, header, csv_content)


def csv_table(key, value, fmt, meta):
    if not check_preconditions(key, value):
        return

    (_, classes, paired_attributes), content = value

    paired_attributes = map_attributes(paired_attributes)

    return get_table(paired_attributes, content)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Include content from CSV files as tables in Pandoc.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-m", "--markdown", action="store_true",
                        help='Parse cell content as markdown')
    parser.add_argument("-v", '--version', action='version', version='%(prog)s 0.1')

    return parser.parse_args()


def main():
    toJSONFilter(csv_table)


if __name__ == '__main__':
    args = parse_arguments()
    main()
