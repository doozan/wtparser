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


def get_template_depth(text, start_depth=0):
    """
    Returns the depth of template templates at the end of the given line

    zero }} zero {{ one {{ two {{ three }} two }} one }} zero }} zero
    """

    if start_depth < 0:
        raise ValueError("start_level cannot be negative")

    depth = start_depth

    first = True
    for t in text.split("{{"):
        if first:
            first = False
            if not depth:
                continue
        else:
            depth += 1

        depth = max(0, depth - t.count("}}"))

    return depth


def template_aware_splitlines(text, keepends=False):
    return template_aware_iterator(text.splitlines(keepends))


def template_aware_split(text, delimiter):
    return template_aware_iterator(text.split(delimiter), delimiter)


def template_aware_iterator(iterator, delimiter=""):
    results = []
    template = []
    template_depth = 0

    for item in iterator:
        if template_depth:
            template.append(item)
            template_depth = get_template_depth(item, template_depth)
            if template_depth:
                continue
            else:
                item = delimiter.join(template)
                template = []

        else:
            template_depth = get_template_depth(item, template_depth)
            if template_depth:
                template = [item]
                continue

        yield item

    if len(template):
        yield delimiter.join(template)


def get_target_def(self, nym_sense):
    """
        Select the best target definition from *defs* for *nym_sense*
        Returns the first matching definition, searching all defs in the following order:
            nym_sense == def.senseid
            nym_sense == def.first_word
            nym_sense in def.words

        If none of the above match, returns the first definition
        """

    target_defs = None
    if nym_sense == "":
        target_defs = self.defs
    else:
        target_defs = self.get_defs_matching_senseid(nym_sense)
        if target_defs:
            self.flag_problem("automatch_senseid")
        else:
            target_defs = self.get_defs_matching_sense(nym_sense)
            if target_defs:
                self.flag_problem("automatch_sense")
            else:
                target_defs = self.get_defs_matching_text(nym_sense)
                if target_defs:
                    self.flag_problem("automatch_sense_text")
                else:
                    self.flag_problem("unmatched_sense")
    #                        target_defs=[self.defs[0]]

    if len(target_defs) > 1:
        self.flag_problem("sense_matches_multiple_defs")

    return target_defs[0]


def parse_anything(value, **params):
    from .wtcode import WTcode

    return WTcode(mwparse_anything(value, **params))
