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

import wiktionaryparser

ALL_LANGUAGES = {
    "English": "en",
    "Spanish": "es",
}

# Nyms will be inserted into definitions according to the order here
# The first tag listed will be used when creating nym tags
ALL_NYMS = {
    "Synonyms": ["syn", "synonyms"],
    "Antonyms": ["ant", "antonyms"],
    "Hyperyms": ["hyper", "hypernyms"],
    "Hyponyms": ["hypo", "hyponyms"],
    "Meronyms": ["meronyms"],
    "Holonyms": ["holonyms"],
    "Troponyms": ["troponyms"],
}
NYM_ORDER = list(ALL_NYMS.keys())

NYM_TO_TAG = {k: v[0] for k, v in ALL_NYMS.items()}
TAG_TO_NYM = {k: v for v, tags in ALL_NYMS.items() for k in tags}
ALL_NYM_TAGS = [ tag for tags in ALL_NYMS.values() for tag in tags ]

ALL_POS = {
    "Abbreviation": "abbr",
    "Acronym": "acronym",
    "Adjectival noun": "adj",
    "Adjective": "adj",
    "Adnominal": "adnominal",
    "Adverb": "adv",
    "Adverbial phrase": "adv",
    "Affix": "affix",
    "Ambiposition": "ambip",
    "Article": "art",
    "Cardinal number": "cardinal num",
    "Cardinal numeral": "cardinal num",
    "Circumfix": "circumfix",
    "Circumposition": "circump",
    "Classifier": "classifier",
    "Clitic": "clitic",
    "Combining form": "affix",
    "Conjugation": "conjugation",
    "Conjunction": "conj",
    "Contraction": "contraction",
    "Counter": "counter",
    "Declension": "declension",
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
    "Ordinal number": "ordinal num",
    "Ordinal numeral": "ordinal num",
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
