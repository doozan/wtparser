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

from . import WiktionaryNode
from .definition import Definition
from ..utils import parse_anything, template_aware_split, template_aware_splitlines

class Word(WiktionaryNode):
    """
    Parses a section containing a headword declaration followed by definitions:
    {{head-noun}}

    # def 1
    #: blah
    # def2
    """

#    def __init__(self, text, name, parent):
#        super().__init__(text, name, parent)

    def _parse_data(self, text):
        self._children = []
        self._parse_list(text)

    def _is_header(self, line):

        if re.match(r"\s+$", line):
            return True

        if not self._heading_found and re.match(r"\s*{{", line):
            self._heading_found=True
            return True

        return False

    def _is_new_item(self, line):
        return re.match(r"\s*# ", line)

    def _is_still_item(self, line):
        return re.match(r"\s*#[^ ]", line)

    def add_item(self, lines):
        item = Definition("".join(lines), name=len(self._children), parent=self)
        self._children.append(parse_anything(item))
