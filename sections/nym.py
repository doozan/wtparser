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
from . import WiktionarySection
from ..wtnodes.nymsense import NymSense
from ..constants import ALL_NYMS
from ..utils import parse_anything, template_aware_splitlines


class NymSection(WiktionarySection):
    def __init__(self, wikt, parent=None):
        self._expected_sections = []
        super().__init__(wikt, parent)

        if self._name not in ALL_NYMS:
            self.flag_problem("section_is_not_nym", self._name)

    def _prepare_line(self, line):
        if line.startswith("{{sense"):
            self.flag_problem("autofix_bad_nymline")
            return "* "+ line
        return line

    def _is_new_item(self, line):
        if line.startswith("*"):
            self._current_sense = NymSense.parse_sense(line)[0]
            return True
        return False

    def _is_still_item(self, line):
        if line.startswith("*:") or line.startswith("**"):
            return True
        if line.startswith("*"):
            sense = NymSense.parse_sense(line)[0]
            # Anything with a declared sense is its own item
            # Lines without a declared sense can be merged together
            return sense == "" and sense == self._current_sense
        return False

    def add_item(self, lines):
        trailing = self.pop_trailing_newlines(lines)

        item = NymSense("".join(lines), name=len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))
        if len(trailing):
            self._children.append(parse_anything(trailing))
        return item
