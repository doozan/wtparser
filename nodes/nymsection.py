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

import os
import re

# import wiktionaryparser
from ..constants import ALL_NYMS
from ..utils import parse_anything, template_aware_splitlines
from .nymsense import NymSense
from . import WiktionarySection


def get_nym_sense(line):
    sense = ""
    res = re.match(r"\*\s*{{s(?:ense)?(\|[^{}]+)}}\s*", line)
    sense = res.group(1) if res else ""
    return sense


class NymSection(WiktionarySection):
    def __init__(self, wikt, parent=None):
        self._expected_sections = []
        super().__init__(wikt, parent)

        if self._name not in ALL_NYMS:
            self.flag_problem("section_is_not_nym", self._name)

        self._parse_data(wikt)

    def _parse_data(self, wikt):
        """
        Parses a wikimarkup section containing a header and an ordered list of wordlinks
        Returns a list of nodes
        """

        data_nodes = wikt._pop_data()
        old_children = self._children
        self._children = []

        section_text = "".join(map(str, data_nodes))

        current_item = []
        unhandled = []

        prev_sense = None
        in_header = True
        in_footer = False

        for unstripped_line in template_aware_splitlines(section_text, True):
            line = unstripped_line.strip()
            if in_footer:
                unhandled.append(unstripped_line)

            elif line == "":
                if current_item:
                    current_item.append(unstripped_line)
                else:
                    unhandled.append(unstripped_line)

            elif in_header:
                unhandled.append(unstripped_line)
                if line.startswith("="):
                    in_header = False
                else:
                    self.flag_problem("text_before_header", line)

            elif line.startswith("*") or line.startswith("{{sense"):

                if line.startswith("{{sense"):
                    line = "* "+line
                    unstripped_line = "* "+unstripped_line
                    self.flag_problem("autofix_bad_nymline")

                if len(unhandled):
                    self.add_text(unhandled)
                    unhandled = []

                sense = get_nym_sense(line)
                if not prev_sense:
                    prev_sense = sense
                elif sense != prev_sense:
                    prev_sense = sense
                    self.add_nymsense(current_item)
                    current_item = []

                current_item.append(unstripped_line)
            else:
                if len(current_item):
                    self.add_nymsense(current_item)
                    current_item = []
                unhandled.append(unstripped_line)
                if (
                    line.startswith("----")
                    or line.startswith("[[Category:")
                    or line.startswith("==")
                ):
                    in_footer = True
                else:
                    self.flag_problem("unhandled_text", line)


        if len(current_item):
            self.add_nymsense(current_item)
            current_item = []
        elif len(unhandled):
            self.add_text(unhandled)
            unparsed = []

        self._children += old_children

    def add_nymsense(self, items):
        item = NymSense("".join(items), name=len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))
        return item
