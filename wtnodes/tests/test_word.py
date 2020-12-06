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

import pytest

from ... import parse
from ...sections.pos import PosSection
from ..word import Word
from ..nymsense import NymSense

def test_simple(language, nymsection):

    orig_text = """===Noun===
{{es-noun|f}}

# {{lb|es|art}} [[caricature]] (pictorial representation of someone for comic effect)
# {{lb|es|colloquial|Mexico}} [[animated cartoon]] (''specially in plural'')

====Synonyms====
* {{sense|caricature}} {{l|es|dibujo}}
* {{sense|cartoon}} {{l|es|dibujos animados}}

====Hyponyms====
* {{l|es|caricatura editorial||editorial cartoon}}
* {{l|es|caricatura política}}

====Blah====
* stuff
"""

    wiki = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wiki, parent=language)

    assert str(pos) == orig_text
    assert pos.name == "Noun"

    words = pos.filter_words(recursive=False)
    assert len(words) == 1

    word = words[0]
#    for child in word._children:
#        print("----------")
#        print(child)
#        for node in child.nodes:
#            print(child.__class__, node.__class__)


    defs = word.filter_wordsenses(recursive=False)
    assert len(defs) == 2

    assert (
        str(word.filter_wordsenses(recursive=False)[0]).strip()
        == "# {{lb|es|art}} [[caricature]] (pictorial representation of someone for comic effect)"
    )
    assert (
        str(word.filter_wordsenses(recursive=False)[1]).strip()
        == "# {{lb|es|colloquial|Mexico}} [[animated cartoon]] (''specially in plural'')"
    )

def test_extra_header(language):
    orig_text="""\
===Noun===
{{es-noun|f|-}}

# [[word1]]
# [[word2]]
"""
    wiki = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wiki, parent=language)

    assert str(pos) == orig_text
    assert pos.name == "Noun"

    defs = pos.filter_wordsenses()
    assert len(defs) == 2


    orig_text="""\
===Noun===
{{wikipedia|lang=es}}
{{es-noun|f|-}}

# [[word1]]
# [[word2]]
"""
    wiki = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wiki, parent=language)

    assert str(pos) == orig_text
    assert pos.name == "Noun"

    defs = pos.filter_wordsenses()
    assert len(defs) == 2


    orig_text="""\
===Noun===
{{es-noun|f|-}}
{{wikipedia|lang=es}}

# [[word1]]
# [[word2]]
"""
    wiki = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wiki, parent=language)

    assert str(pos) == orig_text
    assert pos.name == "Noun"

    words = pos.filter_words()
    print(f"Word: '{words[0]}'")


    defs = pos.filter_wordsenses()
    assert len(defs) == 2


def test_subsenses(language):
    orig_text = """\
===Verb===
{{es-verb|sac|ar|pret=saqué}}

# {{lb|es|reflexive}} to [[obtain]], [[receive]]
## {{lb|es|reflexive}} to [[win]], get, obtain (a prize, award)
##: {{ux|es|Él '''se sacó''' el gordo.|He '''won''' first prize.}}
## {{lb|es|reflexive}} to receive, get, be [[inflict]]ed with
##: {{ux|es|'''Me saqué''' un puñetazo|'''I received''' a punch.}}
##: {{syn|es|syn1}}
"""
    wiki = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wiki, parent=language)

    glosses = pos.filter_glosses()
    assert len(glosses) == 3

    nyms = pos.filter_nymlines()
    assert len(nyms) == 1

def test_verb_forms(language):
    orig_text = """\
===Verb===
{{es-verb|sac|ar|pret=saqué}}

# {{lb|es|reflexive}} to [[obtain]], [[receive]]

====Conjugation====
{{es-conj-ar|sa|p=-car|combined=1}}

"""
    wiki = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wiki, parent=language)

    word = next(pos.ifilter_words())
    assert len(word.forms) == 180


