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
from ..pos import PosSection
from ...wtnodes.nymsense import NymSense

def test_simple(language, nymsection):

    orig_text = """===Noun===
{{es-noun|f}}

# def 1; def2
# def 3

{{es-noun|m}}

# def 4
"""

    wikt = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wikt, parent=language)

    assert str(pos) == orig_text
    assert pos.name == "Noun"

    len(pos.filter_words(recursive=False)) == 2
    assert str(pos.filter_words(recursive=False)[0]).strip() == "{{es-noun|f}}\n\n# def 1; def2\n# def 3"
    assert str(pos.filter_words(recursive=False)[1]).strip() == "{{es-noun|m}}\n\n# def 4"


def test_simple2(language, nymsection):

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

    wikt = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wikt, parent=language)

    synonyms = next(pos.ifilter_nyms(recursive=False, matches="Synonyms"))
    nymsense = next(synonyms.ifilter_senses(recursive=False))
    assert nymsense == "* {{sense|caricature}} {{l|es|dibujo}}\n"
    assert nymsense.sense == "caricature"

    word = pos.filter_words(recursive=False)[0]

#    assert len(word.get_defs_matching_sense(nymsense.sense)) == 1
#    d = word.get_defs_matching_sense(nymsense.sense)[0]
#    assert str(d).strip() == "# {{lb|es|art}} [[caricature]] (pictorial representation of someone for comic effect)"

#    assert "dibujo" not in str(d)
#    d.add_nymsense(nymsense)
#    assert "dibujo" in str(d)
#    assert str(d).strip() == "# {{lb|es|art}} [[caricature]] (pictorial representation of someone for comic effect)\n"\
#            "#: {{syn|es|dibujo}}"

#    new_nym = NymSense("* [[word2]]", name="Synonyms", parent=nymsection)
#    d.add_nymsense(new_nym)
#    assert str(d).strip() == "# {{lb|es|art}} [[caricature]] (pictorial representation of someone for comic effect)\n"\
#            "#: {{syn|es|dibujo|word2}}"


def test_sense_matching(language):
    orig_text="""===Noun===
{{es-noun}}

# {{lb|es|sense1}} [[word1]], [[word2]] {{gloss|gloss1}}
# {{lb|es|sense2}} [[word3]]
# [[word4]]

====Synonyms====
* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}
* {{sense|sense2}} {{l|es|syn3}}
* {{sense|word4}} {{l|es|syn4}}
* {{l|es|syn5}}
"""

    wikt = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wikt, parent=language)
    word = pos.filter_words()[0]

    defs = word.filter_defs()
    assert defs[0] == "# {{lb|es|sense1}} [[word1]], [[word2]] {{gloss|gloss1}}\n"
    assert defs[1] == "# {{lb|es|sense2}} [[word3]]\n"
    assert defs[2] == "# [[word4]]\n"

    senses = pos.filter_senses()
    assert senses[0] == "* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}\n"
    assert senses[0].sense == "sense1"
    assert senses[1] == "* {{sense|sense2}} {{l|es|syn3}}\n"
    assert senses[1].sense == "sense2"
    assert senses[2] == "* {{sense|word4}} {{l|es|syn4}}\n"
    assert senses[2].sense == "word4"
    assert senses[3] == "* {{l|es|syn5}}\n"
    assert senses[3].sense == ""

#    assert word.get_defs_matching_sense(senses[0].sense)[0] == defs[0]
#    assert word.get_defs_matching_sense(senses[1].sense)[0] == defs[1]
#    assert word.get_defs_matching_sense(senses[2].sense)[0] == defs[2]


def test_sense_matching_multi(language):
    orig_text="""===Noun===
{{es-noun}}

# [[word1]], a [[word2]]
# [[word2]]
# [[word3]]

====Synonyms====
* {{sense|word2}} {{l|es|syn1}}
"""

    wikt = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wikt, parent=language)
    word = pos.filter_words()[0]

    assert sorted(language.problems.keys()) == []
    sense = next(pos.ifilter_senses())

    assert sense.sense == "word2"
#    assert len(word.get_defs_matching_sense("word2")) == 2


def xtest_add_sense(language):
    orig_text="""===Noun===
{{es-noun}}

# {{lb|es|sense1}} [[word1]], [[word2]] {{gloss|gloss1}}
# {{lb|es|sense2}} [[word3]]
# [[word4]]

====Synonyms====
* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}
* {{sense|sense2}} {{l|es|syn3}}
* {{sense|word4}} {{l|es|syn4}}
* {{l|es|syn5}}
"""

    wikt = parse(orig_text, skip_style_tags=True)
    pos = PosSection(wikt, parent=language)
    word = pos.filter_words()[0]

    defs = word.filter_defs()
    assert defs[0] == "# {{lb|es|sense1}} [[word1]], [[word2]] {{gloss|gloss1}}\n"
    assert defs[1] == "# {{lb|es|sense2}} [[word3]]\n"
    assert defs[2] == "# [[word4]]\n"

    senses = pos.filter_senses()
    assert senses[0] == "* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}\n"
    assert senses[0].sense == "sense1"
    assert senses[1] == "* {{sense|sense2}} {{l|es|syn3}}\n"
    assert senses[1].sense == "sense2"
    assert senses[2] == "* {{sense|word4}} {{l|es|syn4}}\n"
    assert senses[2].sense == "word4"
    assert senses[3] == "* {{l|es|syn5}}\n"
    assert senses[3].sense == ""

#    assert word.get_defs_matching_sense(senses[0].sense)[0] == defs[0]
#    assert word.get_defs_matching_sense(senses[1].sense)[0] == defs[1]
#    assert word.get_defs_matching_sense(senses[2].sense)[0] == defs[2]


    all_defs = word.filter_defs(recursive=False)
    all_nyms = word.filter_nyms(matches="Synonyms")

    for nym in all_nyms:
        senses = nym.filter_senses()
        for nymsense in senses:
            defs = word.get_defs_matching_sense(nymsense.sense)
            if not len(defs):
                if nymsense.sense == "":
                    defs = all_defs
                else:
                    defs = [ all_defs[0] ]

            d = defs[0]
            d.add_nymsense(nymsense)
        word.remove_child(nym)

    new_text = """===Noun===
{{es-noun}}

# {{lb|es|sense1}} [[word1]], [[word2]] {{gloss|gloss1}}
#: {{syn|es|syn1|syn2|syn5}}
# {{lb|es|sense2}} [[word3]]
#: {{syn|es|syn3}}
# [[word4]]
#: {{syn|es|syn4}}

"""
    assert str(word) == new_text


"""
====Synonyms====
* {{l|es|gabacho}} {{qualifier|Spain, Mexico}}
* {{l|es|guiri}} {{qualifier|Spain}}
#: {{syn|es|gabacho|q1=Spain, Mexico|guiri|q2=Spain}}
"""



