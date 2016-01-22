#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pandoc filter that converts code blocks from listings to minted for LaTeX output.

It is based on:
https://github.com/nick-ulle/pandoc-minted
https://gist.github.com/jepio/3ecaa6bba2a53ff74f2e
"""
import textwrap

from pandocfilters import RawBlock, toJSONFilter, RawInline


def get_attribute(attributes, name):
    for key, value in attributes:
        if key == name:
            return value


def join_attributes(attributes, classes):
    exceptions = ["language", "caption", "minted"]
    result = ['{}="{}"'.format(key, value) for key, value in attributes if key not in exceptions]
    result = result + [key for key in classes if key not in exceptions]
    result = ", ".join(sorted(result))
    if result:
        result = "[" + result + "]"
    return result


def format_code(args):
    minted_simple = """
    \\begin{{minted}}{attributes}{{{language}}}
    {content}
    \\end{{minted}}
    """

    minted_captioned = """
    \\begin{{listing}}[H]
    \\begin{{minted}}{attributes}{{{language}}}
    {content}
    \\end{{minted}}
    \\vspace{{-5pt}}
    \\caption{caption_short}{{{caption_long}}}
    \\end{{listing}}
    """

    minted_inline = "\\mintinline{attributes}{{{language}}}{{{content}}}"

    if args["key"] == "Code":
        template = minted_inline
    elif args["caption_long"]:
        template = minted_captioned
    else:
        template = minted_simple

    template = textwrap.dedent(template).strip()
    return template.format(**args)


def check_preconditions(key, value, meta, **kwargs):
    if key not in ['CodeBlock', 'Code']:
        return False

    classes = value[0][1]
    default_exceptions = ["table", "ditaa", "plantuml"]
    classes_exclude = set(classes).intersection(set(meta.get("minted-exclude", default_exceptions)))
    if classes_exclude:
        return False

    return not meta.get("minted-class", False) or "minted" in classes or key == "Code"


def get_caption(paired_attributes):
    caption_long = get_attribute(paired_attributes, "caption") or ""

    caption_split = caption_long.split("\\autocite")
    if len(caption_split) == 2:
        caption_short = "[{}]".format(caption_split[0].strip())
    else:
        caption_short = ""

    return caption_long, caption_short


def minted(key, value, fmt, meta):
    if not check_preconditions(**locals()):
        return

    (_, classes, paired_attributes), content = value

    language = get_attribute(paired_attributes, "language") or meta.get("minted-language", "text")
    caption_long, caption_short = get_caption(paired_attributes)

    attributes = join_attributes(paired_attributes, classes)

    element = RawInline if key == "Code" else RawBlock

    return [element("latex", format_code(locals()))]


def main():
    toJSONFilter(minted)


if __name__ == "__main__":
    main()
