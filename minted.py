#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pandoc filter that converts code blocks from listings to minted for LaTeX output.

It is based on:
https://github.com/nick-ulle/pandoc-minted
https://gist.github.com/jepio/3ecaa6bba2a53ff74f2e
"""
import argparse
import textwrap

from pandocfilters import RawBlock, toJSONFilter, RawInline

__VERSION__ = "0.1"
__AUTHOR__ = "Julien Hadley Jack <git@jlhj.de>"

def minted(key, value, fmt, meta):
    if not check_preconditions(key, value, meta):
        return

    (_, classes, paired_attributes), content = value

    paired_attributes = map_attributes(paired_attributes)
    settings = generate_settings(paired_attributes, meta, key)
    formatted_attributes = format_attributes(paired_attributes, classes)

    return get_minted(content, key, formatted_attributes, settings)


def check_preconditions(key, value, meta):
    if key not in ['CodeBlock', 'Code']:
        return False

    classes = value[0][1]
    default_exceptions = ["table", "ditaa", "plantuml"]
    classes_exclude = set(classes).intersection(set(meta.get("minted-exclude", default_exceptions)))
    if classes_exclude:
        return False

    return not meta.get("minted-class", False) or "minted" in classes or key == "Code"


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


def generate_settings(paired_attributes, meta, key):
    """
    Generates a settings object containg all the settings from the code and the metadata of the document.

    :param paired_attributes: The attributes of the code.
    :type paired_attributes: dict[str, str]
    :param meta: The metadata of the document.
    :type meta: dict[str, str]
    :return: The settings
    :rtype: dict[str, str | int]
    """
    caption_long, caption_short = get_caption(paired_attributes)
    return {
        "language": paired_attributes.get("language") or meta.get("minted-language") or "text",
        "caption_long": caption_long,
        "caption_short": caption_short,
        "figure_options": get_setting("minted-figure", paired_attributes, meta, "H"),
        "key": key
    }


def get_caption(paired_attributes):
    caption_long = paired_attributes.get("caption", "")

    caption_split = caption_long.split("\\autocite")
    if len(caption_split) == 2:
        caption_short = "[{}]".format(caption_split[0].strip())
    else:
        caption_short = ""

    return caption_long, caption_short


def get_setting(key, paired_attributes, meta=None, default_value="", remove=False):
    """
    Looks at the attributes of the code and the metadata of the document (in that order) and returns the value when it
    finds one with the specified key.

    :param key: The key or keys that should be searched for. Only the result for the first key found will be returned.
    :type key: str | list[str]
    :param paired_attributes: The attributes for the code.
    :type paired_attributes: dict[str, str]
    :param meta: The metadata of the document.
    :type meta: dict[str, str]
    :param default_value: The value that should be found if the key(s) can't be found.
    :type default_value: str | object
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


def format_attributes(attributes, classes):
    exceptions = ["language", "caption", "minted"]
    result = ['{}="{}"'.format(key, value) for key, value in attributes.items() if key not in exceptions]
    result = result + [key for key in classes if key not in exceptions]
    result = ", ".join(sorted(result))
    if result:
        result = "[" + result + "]"
    return result


def get_minted(content, key, formatted_attributes, settings):

    element = RawInline if key == "Code" else RawBlock
    code_block = format_code(content, formatted_attributes, settings)

    return [element("latex", code_block)]


def format_code(content, formatted_attributes, settings):
    minted_simple = """
    \\begin{{minted}}{formatted_attributes}{{{settings[language]}}}
    {content}
    \\end{{minted}}
    """

    minted_captioned = """
    \\begin{{listing}}[{settings[figure_options]}]
    \\begin{{minted}}{formatted_attributes}{{{settings[language]}}}
    {content}
    \\end{{minted}}
    \\vspace{{-5pt}}
    \\caption{settings[caption_short]}{{{settings[caption_long]}}}
    \\end{{listing}}
    """

    minted_inline = '\\mintinline{formatted_attributes}{{{settings[language]}}}{{{content}}}'

    if settings["key"] == "Code":
        template = minted_inline
    elif settings["caption_long"]:
        template = minted_captioned
    else:
        template = minted_simple

    template = textwrap.dedent(template).strip()
    return template.format(**locals())


def parse_arguments():
    """
    Provides a minimal command line interface that shows help text and version information

    :return: The arguments from the command line.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", '--version', action='version', version='%(prog)s ' + __VERSION__)

    return parser.parse_args()


def main():
    """
    This is the main method that gets data from stdin,
    applies the filter and returns the result to stdout.
    """
    toJSONFilter(minted)


if __name__ == "__main__":
    # parse_arguments()
    main()
