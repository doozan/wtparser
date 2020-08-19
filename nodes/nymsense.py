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

from ..utils import parse_anything, template_aware_split, template_aware_splitlines
from . import WiktionaryNode

from .wordlink import WordLink
from .language import LanguageSection


class NymSense(WiktionaryNode):
    def __init__(self, wikt, name, parent, nym_type=None, lang_id=None):
        super().__init__(wikt, name, parent)

        self.lang_id = (
            lang_id if lang_id else self.get_ancestor_value("lang_id", "ERROR")
        )
        self.sense = None

        if nym_type:
            self._type = nym_type
        else:
            from .nymsection import NymSection

            ancestor = self.get_ancestor(NymSection)
            self._type = ancestor.name if ancestor is not None else "ERROR"

        self._parse_data(wikt)

    def _parse_data(self, wikt):
        self._children = []
        text = str(wikt)
        res = re.match(r"\*\s*{{s(?:ense)?\|([^{}\|]+)}}\s*", text)
        self.sense = res.group(1) if res else ""
        # TODO: skip over sense template

        for line in template_aware_splitlines(text, True):
            if line.strip() == "":
                self.add_text(line)
            else:
                self.add_line(line)

    def add_line(self, line):
        """
        Parses a line of words defined within wiki tags
        If a line has multiple words, they must be comma separated
        """

        # Match lines starting with '*' then whitespace then possible '{'
        res = re.match(r"(\*\s*)([^*].*?)(\s*)$", line)
        if not res:
            self.flag_problem("unexpected_line_start", line)
            self.add_text(line)
            return

        start_text = res.group(1)
        line_text = res.group(2)
        trailing_whitespace = res.group(3)

        # TODO: Handle sense tags?
        self.add_text(start_text)
        first = True

        for text in template_aware_split(line_text, ","):
            if first:
                first = False
            else:
                self.add_text(",")
            if text == "":
                self.add_text(",")
                self.flag_problem("empty_item_in_list", line_text)

            # TODO: Better counter
            item = WordLink(text, name=len(self._children) + 1, parent=self)
            self._children.append(parse_anything(item))

        if trailing_whitespace:
            self.add_text(trailing_whitespace)
