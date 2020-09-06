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
from ..wtnodes.word import Word


class PosSection(WiktionarySection):
    """ Parses a Part Of Speech section into Word nodes:
    ===Noun===
    {{es-noun}}

    #def 1
    # def2

    {{es-noun|f=worda}}

    #def 3
    """
#    def __init__(self, wikt, parent=None):
#        super().__init__(wikt, parent, parse_data=False)

    def _is_new_item(self, line):
        # Header can contain a headword template {{head* or {{lang-*
        tmpl_prefix = [ "head", self.lang_id + "-" ]
        if re.match(r"\s*{{\s*("+ "|".join(tmpl_prefix) + ")", line): # }}
            return True
        return False

    def _is_still_item(self, line):
        return line.startswith("#")

    def add_item(self, lines):
        """
        Creates a new Word from the supplied text
        """
        self.add_text(self.pop_leading_newlines(lines))

        trailing_newlines = self.pop_trailing_newlines(lines)
        item = Word("".join(lines), len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))

        self.add_text(trailing_newlines)
