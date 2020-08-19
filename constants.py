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
ALL_NYM_TAGS = TAG_TO_NYM.keys()


ALL_WORDS = (
    "Noun",
    "Verb",
    "Adjective",
    "Adverb",
    "Interjection",
    "Article",
    "Proper noun",
    "Preposition",
    "Numeral",
    "Cardinal number",
    "Ordinal number",
    "Number",
    "Acronym",
    "Determiner",
    "Phrase",
    "Suffix",
    "Pronoun",
    "Conjunction",
    "Proverb",
    "Contradiction",
    "Prefix",
    "Letter",
    "Abbreviation",
    "Initialism",
    "Idiom",
    "Affix",
    "Adverbial phrase",
    "Participle",
    "Contraction"
)
