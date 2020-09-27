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
from .gloss import Gloss
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


    _headwords = {
        "head",
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

    _labels = { "term-label", "tlb" }

    def _parse_data(self, text):
        self.qualifiers = []
        self._children = []
        self._parse_list(text)

    def _parse_header(self, lines):
        """Find and parse the headword declaration"""
        self.add_text(lines)
        self.headword = None

        wikt = parse_anything(lines)
        headwords = wikt.filter_templates(matches = lambda x: str(x.name) in self._headwords)
        if not len(headwords):
            self.flag_problem("headword_missing")
        else:
            # TODO Warn if headword type doesn't match parent POS
            if len(headwords)>1:
                self.flag_problem("multiple_headwords")
            self.headword = headwords[-1]


        # TODO: How should qualifiers be parsed?
        # it's sloppy to call into Gloss
        # it's redundant to have label parsing code in Gloss and enwiktionary_templates
        # but it's silly to require enwiktionary_templates in here (or is it?)

        labels = wikt.filter_templates(matches = lambda x: str(x.name) in self._labels)
        for label in labels:
            self.qualifiers += Gloss.get_label_qualifiers(label)

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

    @property
    def details(self):

        item = {}
        item["pos"] = re.sub(r"\s*[0-9]*$", "", self._parent.name)
        item["shortpos"] = ALL_POS.get(item["pos"], "unknown")
        item["qualifiers"] = self.qualifiers
        item["gender"] = self.gender
#        item["lemma"] = self.lemma
#        item["plural"] = self.lemma

        if self.headword.name == "head":
            item["pos_category"] = str(self.headword.get(2))

        return item

    @property
    def gender(self):
        if not self.headword:
            return None

        targets = []
        if self.headword.name == "head":
            targets = [
                ["g", "gen", "g1"],
                ["g2"],
                ["g3"],
                ]

        # FIXME: hardcoded language id
        elif self.headword.name in ["es-noun", "es-proper noun"]:
            targets = [
                ["1", "g", "gen", "g1"],
                ["g2"],
                ["g3"],
                ]

        genders = []
        for params in targets:
            gender = None
            for p in params:
                if self.headword.has(p):
                    gender = str(self.headword.get(p).value).replace("-", "")
            if gender and gender not in genders:
                genders += gender

        return "".join(genders)
