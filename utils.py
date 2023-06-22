#
# Copyright (c) 2020 Jeff Doozan
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__all__ = [
    "parse_anything",
    "get_template_depth",
    "template_aware_splitlines",
    "template_aware_split",
]

from mwparserfromhell.utils import parse_anything as mwparse_anything
import re

def parse_anything(value, **params):
    from .wtcode import WTcode

    return WTcode(mwparse_anything(value, **params))

def get_template_depth(text, start_depth=0):
    """
    Returns the depth of template templates at the end of the given line
    zero }} zero {{ one {{ two {{ three }} two }} one }} zero }} zero
    """

    return get_nest_depth(text, "{{", "}}", start_depth=start_depth)

def get_nest_depth(text, opener, closer, start_depth=0):
    """ Returns the level of depth inside ```start``` at the end of the line
    opener and closer are the nest opening and closing strings
    starting_depth, optional is the starting depth level

    zero }} zero {{ one {{ two {{ three }} two }} one }} zero }} zero
    """

    if start_depth < 0:
        raise ValueError("start_level cannot be negative")

    depth = start_depth

    first = True
    for t in text.split(opener):
        if first:
            first = False
            if not depth:
                continue
        else:
            depth += 1

        depth = max(0, depth - t.count(closer))

    return depth

def nest_aware_iterator(iterator, nests, delimiter=""):
    results = []
    items = []
    depth = {}

    for item in iterator:
        items.append(item)
        depth = { nest:get_nest_depth(item, nest[0], nest[1], depth.get(nest, 0)) for nest in nests }
        if any(depth.values()):
            continue

        yield delimiter.join(items)
        items = []

    if len(items):
        yield delimiter.join(items)

def nest_aware_resplit(pattern, text, nests, flags=re.DOTALL):

    if not pattern.startswith("("):
        pattern = "(" + pattern + ")"

    results = []
    items = []
    depth = {}

    it = iter(re.split(pattern, text, flags))
    for item in it:
        delimiter = next(it,"")
        items.append(item)
        depth = { nest:get_nest_depth(item, nest[0], nest[1], depth.get(nest, 0)) for nest in nests }
        if any(depth.values()):
            items.append(delimiter)
            continue

        yield ("".join(items), delimiter)
        items = []

    if len(items):
        yield (delimiter.join(items), "")

def nest_aware_splitlines(text, nests, keepends=False):
    return nest_aware_iterator(text.splitlines(keepends), nests)

def nest_aware_split(delimiter, text, nests):
    return nest_aware_iterator(text.split(delimiter), nests, delimiter)

def nest_aware_index(delimiter, text, nests):
    part = next(nest_aware_split(delimiter, text, nests), None)
    if len(part)==len(text):
        return -1

    return len(part)

def nest_aware_contains(delimiter, text, nests):
    return nest_aware_index(delimiter, text, nests) != -1

def template_aware_splitlines(text, keepends=False):
    return nest_aware_iterator(text.splitlines(keepends), [("{{","}}")])

def template_aware_split(delimiter, text):
    return nest_aware_iterator(text.split(delimiter), [("{{","}}")], delimiter)

def template_aware_resplit(pattern, text):
    return nest_aware_resplit(pattern, text, [("{{","}}")])

def get_label_qualifiers(t):
    return [ str(p) for p in t.params if p.name != "1" and str(p.name).isdigit() ]


def wiki_finditer(pattern, text, flags=0, ignore_comments=False, ignore_nowiki=False, ignore_templates=False):
    """
    matches pattern within wiki formatted text, with basic awareness
    of templates, html comments and <nowiki> tags
    """

    in_comment = None
    in_nowiki = None
    template_depth = []

    separators = []
    if not ignore_comments:
        separators += ["<!--", "-->"]
    if not ignore_nowiki:
        separators += ["<nowiki>", "</nowiki>"]
    if not ignore_templates:
        separators += [r"(?<!\\)({{|}})"]

    if pattern in separators:
        raise ValueError(f"Invalid search value: {start}")

    if separators:
        pattern = "(" + pattern + "|(?P<_sep>" + "|".join(separators) + "))"

    start_pos = None
    for m in re.finditer(pattern, text, flags):

        if not separators or not m.group('_sep'):
            if in_comment or in_nowiki or template_depth:
                continue
            yield m

        elif in_comment and m.group('_sep') == "-->":
            in_comment = None

        elif in_nowiki and m.group('_sep') == "</nowiki>":
            in_nowiki = None

        elif not ignore_templates and (template_depth and m.group('_sep') == "}}"):
            template_depth.pop()

        elif not ignore_templates and m.group('_sep') == "{{":
            template_depth.append(m)

        elif not ignore_comments and m.group('_sep') == "<!--":
            in_comment = m

        elif not ignore_nowiki and m.group('_sep') == "<nowiki>":
            in_nowiki = m

def wiki_search(text, start, end=None, end_required=False, *args, **kwargs):
    """ Returns matching substrings within text
    If end is provided, returns text between matching start pattern and the end pattern
    If end is not provided, returns text between start pattern and the next start pattern
    """

    pattern = f"(?P<start>{start})"
    if end:
        pattern += f"|(?P<end>{end})"
    else:
        end_required = False

    start_pos = None
    for m in wiki_finditer(pattern, text, re.MULTILINE, *args, **kwargs):

        if m.group('start'):
            if start_pos and not end_required:
                yield m.string[start_pos.start():m.start()]
                start_pos = m

            if not start_pos:
                start_pos = m

        elif end and m.group('end'):
            if not start_pos:
                continue

            yield m.string[start_pos.start():m.end()]
            start_pos = None


    if start_pos and not end_required:
        yield m.string[start_pos.start():]
