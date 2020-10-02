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
from ..utils import parse_anything, template_aware_split, template_aware_splitlines, get_label_qualifiers
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

    # FIXME: hardcoded language keys
    _headwords = {
        "head",
        "en-interj",
        "pt-proper noun",

        "es-adj",
        "es-adj-inv",
        "es-adv",
        "es-conjunction",
        "es-diacritical mark",
        "es-interj",
        "es-interjection",
        "es-letter",
        "es-noun",
        "es-past participle",
        "es-phrase",
        "es-prefix",
        "es-proverb",
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

        labels = wikt.filter_templates(matches = lambda x: str(x.name) in self._labels)
        for label in labels:
            self.qualifiers += get_label_qualifiers(label)

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
    def pos(self):
        return re.sub(r"\s*[0-9]*$", "", self._parent.name.strip())

    @property
    def pos_category(self):
        if self.headword is None:
            return ""
        return str(self.headword.get(2)) if self.headword.name == "head" else ""

    @property
    def shortpos(self):
        return ALL_POS.get(self.pos, "unknown")

    gender_sources = {
        "head": {
            "g": ["g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "es-noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "es-proper noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
    }

    form_sources = {
        "es-adj": {
            "m": ["m"],
            "f": ["f", "f2"],
            "pl": ["pl", "pl2"],
            "mpl": ["mpl", "mpl2"],
            "fpl": ["fpl", "fpl2"]
        },
        "es-noun": {
            "m": ["m", "m2"],
            "f": ["f", "f2"],
            "pl": [2, "pl2"],
            "mpl": ["mpl", "mpl2"],
            "fpl": ["fpl", "fpl2"]
        },
        "es-proper noun": {
            "m": ["m", "m2"],
            "f": ["f", "f2"],
            "pl": [2, "pl2"],
            "mpl": ["mpl", "mpl2"],
            "fpl": ["fpl", "fpl2"]
        },
    }

    @property
    def genders(self):
        if self.headword is None:
            return []
        t = self.headword
        sources = self.gender_sources.get(str(t.name))
        if not sources:
            return []

        res = {}
        for k,params in sources.items():
            for param in params:
                if t.has(param):
                    res[k] = res.get(k, []) + [str(t.get(param).value)]

        return [ v[0] for v in res.values() ]

    @property
    def forms(self):
        if self.headword is None:
            return {}

        t = self.headword
        sources = self.form_sources.get(str(t.name))
        if not sources:
            return {}

        res = {}
        for k,params in sources.items():
            for param in params:
                if t.has(param):
                    res[k] = res.get(k, []) + [str(t.get(param).value)]

        return res

#    @property
#    def lemma(self):
#        if not self.headword:
#            return None

#        if self.headword.name == "es-conj":




