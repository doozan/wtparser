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

def nest_aware_resplit(pattern, text, nests):

    if not pattern.startswith("("):
        pattern = "(" + pattern + ")"

    results = []
    items = []
    depth = {}

    it = iter(re.split(pattern, text, re.DOTALL))
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
        yield delimiter.join(items)

def nest_aware_splitlines(text, nests, keepends=False):
    return nest_aware_iterator(text.splitlines(keepends), nests)

def nest_aware_split(delimiter, text, nests):
    return nest_aware_iterator(text.split(delimiter), nests, delimiter)

def template_aware_splitlines(text, keepends=False):
    return nest_aware_iterator(text.splitlines(keepends), [("{{","}}")])

def template_aware_split(delimiter, text):
    return nest_aware_iterator(text.split(delimiter), [("{{","}}")], delimiter)

def template_aware_resplit(pattern, text):
    return nest_aware_resplit(pattern, text, [("{{","}}")])

