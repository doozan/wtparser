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
from .decoratedlink import DecoratedLink
from ..utils import parse_anything, nest_aware_resplit, template_aware_split, template_aware_splitlines

class NymSense(WiktionaryNode):
    def __init__(self, text, name, parent, nym_type=None):

        self.sense = None
        super().__init__(text, name, parent)

        if nym_type:
            self._type = nym_type
        else:
            from ..sections.nym import NymSection

            ancestor = self.get_ancestor(NymSection)
            self._type = ancestor.name if ancestor is not None else "ERROR"

    def _parse_data(self, text):
        """
        Accepts single line with optional sense tag
        * {{sense|text}} {{l|es|word1}}

        or, multiline with no sense
        * [[word1]], [[word2]]
        * [[word3]]
        """

        self._children = []
        text = self.store_line_start(text)

        trailing = []
        self.sense, source, consumed = self.parse_sense(text)
        if source == "gloss":
            self.flag_problem("autofix_gloss_as_sense")
        elif source == "text":
            self.flag_problem("autofix_parenthetical_as_sense")
        if consumed:
            consumed_text = re.escape(consumed)
            res = re.match(fr"(.*?)({consumed_text})(.*?)(\s*)$", text, re.DOTALL)
            if not res:
                raise ValueError(f"Can't find '{consumed_text}' in: {text}")

            before_sense = res.group(1)
            sense = res.group(2)
            after_sense = res.group(3)
            if res.group(4):
                trailing.insert(0,res.group(4))

            if after_sense and after_sense.strip():
                if before_sense and after_sense.strip():
                    self.flag_problem("sense_in_middle", sense, text)
                    text = before_sense + after_sense
                    self.add_text(sense)
                else:
                    text = after_sense
                    self.add_text(before_sense+sense)
            else:
                text = before_sense
                trailing.insert(0, sense+after_sense)

        first = True
        for line in template_aware_splitlines(text, True):
            if first:
                first=False
            else:
                line = self.store_line_start(line)

            res = re.match(r"(.*?)(\s*)$", line, re.DOTALL)
            if res.group(1):
                self.add_list(res.group(1))
            if res.group(2):
                self.add_text(res.group(2))

        if trailing:
            self.add_text(trailing)

        items = [decoratedlink.item for decoratedlink in self.filter_decoratedlinks()]
        if not len(items):
            self.flag_problem("no_links_in_nymsense", self)

    def store_line_start(self, line):
        """ Put the beginning of the line into _children and return the remainder """
        start_pattern = r"\*[\*:]*\s*"
        res = re.match(f"({start_pattern})(.*)", line, re.DOTALL)
        if not res:
            self.flag_problem("unparsable_nymsense", line)
            self.add_text(line)
            return ""

        self.add_text(res.group(1))
        return res.group(2)


    def add_list(self, line):
        """
        Parses a list of words defined within wiki tags
        If a list has multiple words, they must be comma separated
        """

        prev_delimiter = None
        for text,delimiter in nest_aware_resplit(r"[\/,;]", line, [("{{","}}"), ("(", ")")]):
            if prev_delimiter is not None:
                self.add_text(prev_delimiter)
            prev_delimiter = delimiter
            if text == "":
                self.add_text(delimiter)
                self.flag_problem("empty_item_in_list", line)

            # TODO: Better counter
            item = DecoratedLink(text, name=len(self._children) + 1, parent=self)
            self._children.append(parse_anything(item))

#        if trailing_whitespace:
#            self.add_text(trailing_whitespace)

    @staticmethod
    def parse_sense(line):
        """ Detects the sense, if any, in a nym line

        Returns a tuple (sense, source, consumed)
        sense is the sense detected
        source is "template", "gloss", or "text" and
        consumed is the portion of the line consumed by the detected sense
        """
        wikt = parse_anything(line)

        templates = wikt.filter_templates(matches=lambda x: x.name in ["s", "sense"])

        sense = ""
        source = None
        consumed = None

        if templates:
            source = "template"
        else:
            templates = wikt.filter_templates(matches=lambda x: x.name in ["gl", "gloss"])
            if templates:
                source = "gloss"
#                self.flag_problem("autofix_gloss_as_sense", line)
            if not templates:
                # Match text inside parentheses () at start of line unless it contains a template
                pattern = r"""(?x)
                \*?             # Opening * (optional)
                \s*             # leading whitespace
                (?:\'{2,})?     # two or more ' marks for formatting (optional)
                \(              # opening (
                ([^{})]*)         # contents
                \)              # closing )
                \:*             # : (optional)
                (?:\'{2,})?     # two or more ' marks for formatting (optional)
                """
                res = re.match(pattern, line)
                if res:
                    source = "text"
                    consumed = res.group(0)
#                    self.flag_problem("autofix_parenthetical_as_sense", line)
                    sense = res.group(1).strip("'").strip('"')

        if templates:
#            if len(templates) > 1:
#                self.flag_problem("multiple_sense_templates", line)

            consumed = str(templates[0])
            senses = set( str(p.value) for p in templates[0].params )
            sense = "|".join(senses)

        return (sense, source, consumed)

