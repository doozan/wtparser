#
# from ..constants import SECTION_TYPES
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

"""
This will parse a section containing a wiktionary word
Currently handles word definition and nym sections
"""

import re

from . import WiktionarySection
from .language import LanguageSection
from ..utils import parse_anything, template_aware_splitlines
from ..wtnodes.definition import Definition


class PosSection(WiktionarySection):
    def __init__(self, wikt, parent=None):
        super().__init__(wikt, parent, parse_data=False)
        self._parse_data(wikt)

    def _is_header(self, line):

        if re.match(r"\s+$", line):
            return True

        if line.startswith("==") and not self._heading_found:
            self._heading_found=True
            return True

        if self._is_headword(line):
            return True

        return False

    def _is_headword(self, line):
        # Header can contain a headword template {{head* or {{lang-*
        tmpl_prefix = [ "head", self.lang_id + "-" ]
        if re.match(r"\s*{{\s*("+ "|".join(tmpl_prefix) + ")", line): # }}
            return True
        return False

    def _is_new_item(self, line):
        if line.startswith("# ") or line.startswith("#{"):
            return True
        return False

    def _is_still_item(self, line):
        if line.startswith("# ") or line.startswith("#{"):
            return False
        elif line.startswith("#"):
            return True
        return False

    def _handle_other(self, line):

        # Word declaration
        if self._is_headword(line):

            # Some articles list multiple parts of speech or etymology without breaking them into sections.
            # If we encounter a new declaration, flag it for manual review
            self.flag_problem("word_has_multiple_headwords", line)
            return False

        else:
            return super()._handle_other(line)

    def add_item(self, lines):
        """
        Creates a new Definition from the supplied text
        Returns an array [ leading_newlines, Definition, trailing_newlines ]
        """
        self.add_text(self.pop_leading_newlines(lines))

        trailing_newlines = self.pop_trailing_newlines(lines)
        item = Definition("".join(lines), len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))

        self.add_text(trailing_newlines)

    def get_defs_matching_sense(self, nym_sense):
        return self.filter_defs(
            recursive=False, matches=lambda d: d.has_sense(nym_sense)
        )
