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
from .wordsense import WordSense
from ..utils import parse_anything, template_aware_split, template_aware_splitlines
from ..constants import ALL_POS

class Word(WiktionaryNode):
    """
    Parses a section containing a headword declaration followed by definitions:
    {{head-noun}}
    {{wikipedia|lang=es}}

    # def 1
    #: blah
    # def2
    """

    def _parse_data(self, text):
        self._children = []
        self._parse_list(text)

    def _parse_header(self, lines):
        """Find and parse the headword declaration"""
        self.add_text(lines)
        self.headword = None

        for line in lines:
            res = re.match(r"\s*{{\s*([^|}]+)*", line)
            if not res:
                continue

            tmpl_name = res.group(1).strip()
            if self._is_headword(tmpl_name):
                self.add_headword(line)

        if not self.headword:
            self.flag_problem("headword_missing")

    def _is_header_extra(self, line):
        # Consider any bare template to be part of the header
        return re.match(r"\s*{{", line)

    def _is_new_item(self, line):
        return re.match(r"\s*[#]+[^#:*]", line)

    def _is_still_item(self, line):
        return re.match(r"\s*[#]+[:*]", line)

    def add_item(self, lines):
        item = WordSense("".join(lines), name=len(self._children), parent=self)
        self._children.append(parse_anything(item))

    # TODO Create per-language definitions for this stuff
    _headwords = {
        "en-interj",
        "pt-proper noun",

        "es-adj",
        "es-adj-inv",
        "es-adv",
        "es-diacritical mark",
        "es-interj",
        "es-letter",
        "es-noun",
        "es-past participle",
        "es-phrase",
        "es-proper noun",
        "es-punctuation mark",
        "es-suffix",
        "es-verb"
        }

    def _is_headword(self, name):
        """Returns True if ```name``` is a headword template"""
        if name == "head":
            return True

        # TODO Get parent language and use that for matching headword
        return name in self._headwords

    def add_headword(self, line):
        templates = parse_anything(line).filter_templates(recursive=False)
        if not len(templates):
            raise ValueError(f"No template found in '{line}'")
        if len(templates)>1:
            self.flag_problem("headword_multiple_templates", self.headword, line)

        if self.headword and self.headword != templates[0]:
            self.flag_problem("multiple_headwords", self.headword, line)

        # TODO Warn if headword type doesn't match parent POS
        self.headword = templates[0]

    @property
    def details(self):

        item = {}
        item["pos"] = re.sub(r"\s*[0-9]*$", "", self._parent.name)
        item["shortpos"] = ALL_POS.get(item["pos"], "unknown")

        if not self.headword:
            return item

        targets = {}
        if self.headword.name == "head":
            targets = {
                "g": ["g", "gen", "g1"],
                "g2": ["g2"],
                "g3": ["g3"],
                "pos_category": ["2"]
                 }

        elif self.headword.name in ["es-noun", "es-proper noun"]:
            targets = {
                "g": ["1", "g", "gen", "g1"],
                "g2": ["g2"],
                "g3": ["g3"],
                "plural": ["2"]
                 }

        for k,params in targets.items():
            for p in params:
                if self.headword.has(p):
                    item[k] = str(self.headword.get(p).value)

        genders = []
        for g in ["g", "g2", "g3"]:
            gender = item.get(g, "").replace("-", "")
            if gender and gender not in genders:
                genders += gender
            item["gender"] = "".join(genders)

        return item
