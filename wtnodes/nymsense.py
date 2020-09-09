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
from .wordlink import WordLink
from ..utils import parse_anything, template_aware_split, template_aware_splitlines

class NymSense(WiktionaryNode):
    def __init__(self, text, name, parent, nym_type=None):

        self.sense = None
        super().__init__(text, name, parent)

        if nym_type:
            self._type = nym_type
        else:
            from ..sections.nymsection import NymSection

            ancestor = self.get_ancestor(NymSection)
            self._type = ancestor.name if ancestor is not None else "ERROR"


    def _parse_data(self, text):
        self._children = []
        wikt = parse_anything(text)
        templates = wikt.filter_templates(matches=lambda x: x.name in ["s", "sense"])

        if not templates:
            if re.match(r"(\*\s*){{gl(oss)?\|", text):
                self.flag_problem("autofix_gloss_as_sense", text)
                templates = wikt.filter_templates(matches=lambda x: x.name in ["gl", "gloss"])

        if templates:
            senses = set( str(p.value) for t in templates for p in t.params )
            self.sense = "|".join(senses)
        else:
            self.sense = ""

        skip_templates = set( str(t.name) for t in templates )

        for line in template_aware_splitlines(str(wikt), True):
            if line.strip() == "":
                self.add_text(line)
            else:
                self.add_line(line, skip_templates)

        items = [wordlink.item for wordlink in self.filter_wordlinks()]
        if not len(items):
            self.flag_problem("no_links_in_nymsense", self)

    def add_line(self, line, skip_templates=None):
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
            item = WordLink(text, name=len(self._children) + 1, parent=self, skip_templates=skip_templates)
            self._children.append(parse_anything(item))

        if trailing_whitespace:
            self.add_text(trailing_whitespace)
