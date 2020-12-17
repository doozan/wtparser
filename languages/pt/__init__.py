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

"""
Data and utilities for processing Portugues sections of enwiktionary
"""

import sys
from .. import LanguageData

class Data(LanguageData):

    headwords = {
        "pt-adj",
        "pt-adj-comp",
        "pt-adj-infl",
        "pt-adj-sup",
        "pt-adv",
        "pt-article",
        "pt-cardinal",
        "pt-con",
        "pt-cont",
        "pt-interj",
        "pt-letter",
        "pt-noun",
        "pt-ordinal",
        "pt-phrase",
        "pt-pp",
        "pt-prefix",
        "pt-prep",
        "pt-pron",
        "pt-proper noun",
        "pt-proper-noun",
        "pt-suffix",
        "pt-verb",
        "pt-verb-form-of",
    }

    gender_sources = {
        "head": {
            "g": ["g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "pt-noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "pt-proper noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "pt-proper-noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
    }

    form_sources = {
        "pt-proper noun": {
            "m": ["m", "m2", "m3"],
            "f": ["f", "f2", "f3"],
            "pl": ["pl", "pl2", "pl3"],
            "mpl": ["mpl", "mpl2", "mpl2"],
            "fpl": ["fpl", "fpl2", "mpl3"]
        },
        "pt-proper-noun": {
            "m": ["m", "m2", "m3"],
            "f": ["f", "f2", "f3"],
            "pl": ["pl", "pl2", "pl3"],
            "mpl": ["mpl", "mpl2", "mpl2"],
            "fpl": ["fpl", "fpl2", "mpl3"]
        },
    }

    @classmethod
    def get_form_sources(cls, word):
        template = word.headword
        if template is None:
            return []

        elif str(template.name) == "pt-verb":
            return cls.get_verb_form_sources(word)

        return [template]

    @classmethod
    def get_verb_form_sources(cls, word):
        if not word or not word.headword:
            return []
        return [word.headword] + list(cls.get_conjugation_templates(word))

    @classmethod
    def get_conjugation_templates(cls, word):
        """ Find all conjugation templates for word """

        # Find the nearest ancestor with a Conjugation section
        matcher = lambda x: callable(getattr(x, "filter_sections", None)) and \
                any(x.filter_sections(matches=lambda y: y.name.strip().startswith("Conjugation")))
        ancestor = word.get_matching_ancestor(matcher)
        if not ancestor:
            if " " not in word.page_title and not word.page_title.endswith("se"):
                print("\nNo conjugations", word.page_title, file=sys.stderr)
            return []

        for conjugation in ancestor.ifilter_sections(matches=lambda x: x.name.strip().startswith("Conjugation")):
            for t in conjugation.ifilter_templates(matches=lambda x: x.name.strip().startswith("pt-conj")):
                yield t

