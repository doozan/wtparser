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

ALL_POS = {
    "Abbreviation": "abbr",
    "Acronym": "acronym",
    "Adjective": "adj",
    "Adjectival noun": "adj",
    "Adnominal": "adnominal",
    "Adverb": "adv",
    "Adverbial phrase": "adv",
    "Affix": "affix",
    "Ambiposition": "ambip",
    "Article": "art",
    "Cardinal number": "cnum",
    "Cardinal numeral": "cnum",
    "Circumfix": "circumfix",
    "Circumposition": "circump",
    "Classifier": "classifier",
    "Clitic": "clitic",
    "Combining form": "affix",
    "Conjunction": "conj",
    "Contraction": "contraction",
    "Counter": "counter",
    #"Declension": "declension",
    "Determiner": "determiner",
    "Diacritical mark": "diacrit",
    "Enclitic Particle": "particle",
    "Gerund": "v",
    "Han character": "han",
    "Hanja": "hanja",
    "Hanzi": "han",
    "Idiom": "idiom",
    "Infix": "interfix",
    "Initialism": "initialism",
    "Interfix": "interfix",
    "Interjection": "interj",
    "Kanji": "kanji",
    "Letter": "letter",
    "Ligature": "ligature",
    "Logogram": "logogram",
    "Noun": "n",
    "Number": "num",
    "Numeral": "num",
    "Ordinal number": "onum",
    "Ordinal numeral": "onum",
    "Participle": "v",
    "Particle": "particle",
    "Phrase": "phrase",
    "Postposition": "postp",
    "Predicate": "pred",
    "Predicative": "pred",
    "Prefix": "prefix",
    "Prepositional phrase": "prep",
    "Preposition": "prep",
    "Pronoun": "pron",
    "Proper noun": "prop",
    "Proverb": "proverb",
    "Punctuation mark": "punct",
    "Punctuation": "punct",
    "Relative": "relative",
    "Romanization": "rom",
    "Romanizations": "rom",
    "Root": "root",
    "Stem": "stem",
    "Suffix": "suffix",
    "Syllable": "syllable",
    "Symbol": "symbol",
    "Verbal noun": "n",
    "Verb": "v",
    "Word": "unk",
}

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

    _pos_pattern = "|".join(ALL_POS.keys()) + r'\s*[0-9]*$'

    @classmethod
    def matches_title(cls, title):
        """ Returns True if title matches a section this class can handle """
        return re.match(cls._pos_pattern, title.capitalize())

    def _is_new_item(self, line):
        # Header can contain a headword template {{head* or {{lang-*
        # FIXME: get language specific templates from someplace
        tmpl_prefix = [ "head", self.lang_id + "-", "..-" ]
        if re.match(r"\s*{{\s*("+ "|".join(tmpl_prefix) + ")", line): # }}
            return True
        return False

    def _is_still_item(self, line):
        if self._is_filler_line(line):
            return True
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


