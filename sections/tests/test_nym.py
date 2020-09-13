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

from ... import parse
from ..nym import NymSection

def test_simple_nym():
    orig_text="""===Synonyms===
* {{sense|word}} {{l|es|otherword}}
"""
    expected_text = "{{syn|es|otherword}}"
    expected_flags = []

    wiki = parse(orig_text, skip_style_tags=True)
    nym = NymSection(wiki, parent=None)
    assert nym.name == "Synonyms"
    #assert nym.tag == "{{syn|es|word1|word2}}"

    # TODO: Check that there are nymsenses

def run_test(orig_text, expected_text, expected_flags):

    fixer._flagged = {}
    new_text = fixer.run_fix(orig_text, [], "test")
    assert orig_text == new_text
    #    assert sorted(expected_flags) == sorted(fixer._flagged.keys())

    fixer._flagged = {}
    new_text = fixer.run_fix(
        orig_text, expected_flags, "test", sections=["Synonyms", "Antonyms", "Hyponyms"]
    )
    assert expected_text == new_text


def test_simple(language):
    orig_text = """===Synonyms===
* {{sense|word}} {{l|es|otherword}}
"""
    expected_text = "{{syn|es|otherword}}"
    expected_flags = []

    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)

    assert nymsection.name == "Synonyms"
    decoratedlinks = nymsection.filter_decoratedlinks()
    assert len(decoratedlinks) == 1
    assert len(nymsection.filter_senses(recursive=False)) == 1
    nymsense = next(nymsection.ifilter_senses(recursive=False))
    assert nymsense.sense == "word"
    #assert nymsense.make_tag() == expected_text


def test_complex(language):
    orig_text = """===Synonyms===
* {{l|es|nym1}} {{q|blah1}}
* {{l|es|nym2}} (blah2)
* {{l|es|nym3}} {{qualifier|blah3}}
* [[nym4] (blah4)
* [[nym5|more stuff]] (blah5)
"""
    expected_text = "{{syn|es|nym1|q1=blah1|nym2|q2=blah2|nym3|q3=blah3|nym4|q4=blah4|nym5|q5=blah5}}"
    expected_flags = []

    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)
    assert nymsection.name == "Synonyms"
    decoratedlinks = nymsection.filter_decoratedlinks()
    assert len(decoratedlinks) == 5
    nymsense = next(nymsection.ifilter_senses(recursive=False))
    assert nymsense.sense == ""
#    assert nymsense.make_tag() == expected_text


def test_multiline(language):
    orig_text = """===Synonyms===
* {{l|es|nym1}} {{q|blah1}}, {{l|es|nym2}} (blah2), {{l|es|nym3}} {{qualifier|blah3}}, [[nym4] (blah4), [[nym5|more stuff]] (blah5)
"""
    expected_text = "{{syn|es|nym1|q1=blah1|nym2|q2=blah2|nym3|q3=blah3|nym4|q4=blah4|nym5|q5=blah5}}"
    expected_flags = []

    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)
    assert nymsection.name == "Synonyms"
    decoratedlinks = nymsection.filter_decoratedlinks()
    assert len(decoratedlinks) == 5
    nymsense = next(nymsection.ifilter_senses(recursive=False))
    assert nymsense.sense == ""
    #assert nymsense.make_tag() == expected_text


def test_multisense(language):
    orig_text = """====Synonyms====
* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}
* {{sense|sense2}} {{l|es|syn3}}
* {{l|es|syn4}}
"""
    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)
    assert nymsection.name == "Synonyms"
    senses = nymsection.filter_senses()
    assert len(senses) == 3

    assert senses[0] == "* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}\n"
    assert senses[1] == "* {{sense|sense2}} {{l|es|syn3}}\n"
    assert senses[2] == "* {{l|es|syn4}}\n"


def test_sense_breaks(language):
    orig_text = """====Synonyms====
* {{l|es|word1}}
* {{l|es|word2}}
* {{sense|sense1}} {{l|es|word3}}
"""
    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)
    assert nymsection.name == "Synonyms"
    senses = nymsection.filter_senses()
    assert len(senses) == 2

    assert senses[0] == "* {{l|es|word1}}\n* {{l|es|word2}}\n"
    assert senses[1] == "* {{sense|sense1}} {{l|es|word3}}\n"


def test_qualifiers(language):
    orig_text = """====Synonyms====
* {{l|es|word1}} {{qualifier|q1, q2}}
"""
    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)
    assert nymsection.name == "Synonyms"
    senses = nymsection.filter_senses()
    assert len(senses) == 1

    assert senses[0] == "* {{l|es|word1}} {{qualifier|q1, q2}}\n"

def test_subsections(language):
    orig_text = """===Synonyms===
* {{l|es|word1}} {{qualifier|q1, q2}}

====Subsection====
# blah
"""
    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)

    assert sorted(nymsection.problems.keys()) == sorted(["unexpected_section"])

def test_badline(language):
    orig_text = """===Synonyms===
{{sense|blah}} {{l|es|word1}} {{qualifier|q1, q2}}
"""
    wiki = parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(wiki, parent=language)

    assert sorted(nymsection.problems.keys()) == sorted(["autofix_bad_nymline"])



def xtest_table():
    orig_text = """====Hyponyms====
{{col3|es
|grupo abeliano
|grupo corona
|grupo de la muerte
|grupo étnico
|{{l|es|grupo de presión||lobby, pressure group}}
|{{l|es|grupo de edad||age group, age range, age bracket}}
|grupo funcional
|grupo saliente
|grupo social
}}
"""
    expected_flags = [
        "nymsection_link_unexpected_template",
        "nymsection_missing_link",
        "nymsection_nym_missing_link",
    ]

    wiki = mwparserfromhell.parse(orig_text, skip_style_tags=True)
    nymsection = NymSection(err, "nymsection_", wiki, "es")
    assert nymsection.title == "Hyponyms"
    assert len(nymsection.nyms) == 1
    assert nymsection.nyms[0].sense == ""
    assert nymsection.nyms[0].tag == None

    assert sorted(expected_flags) == sorted(err.errors.keys())


def test_multisense2():
    orig_text="""\
===Synonyms===
* {{l|es|frío}} {{g|m}} (Cuba, colloquial)
* {{l|es|heladera}} {{g|f}} (Argentina, Paraguay, Uruguay)
* {{l|es|nevera}} {{g|f}} (Colombia, Dominican Republic, Puerto Rico, Spain, Venezuela)
"""

    wiki = parse(orig_text, skip_style_tags=True)
    nym = NymSection(wiki, parent=None)
    assert str(nym) == orig_text

    decoratedlinks = nym.filter_decoratedlinks()
    assert decoratedlinks[0] == "{{l|es|frío}} {{g|m}} (Cuba, colloquial)"
    assert decoratedlinks[1] == "{{l|es|heladera}} {{g|f}} (Argentina, Paraguay, Uruguay)"


def test_parenthesis():
    orig_text="""\
===Synonyms===
* (''boiling''): {{l|es|ebullición}}
* (''liveliness''): {{l|es|ánimo}}, {{l|es|fogosidad}}, {{l|es|viveza}}
* (''animosity''): {{l|es|ardor}}, {{l|es|enemistad}}, {{l|es|hostilidad}}
* (''zeal''): {{l|es|celo}}
* (''vehemence''): {{l|es|ahínco}}, {{l|es|eficacia}}
"""

    wiki = parse(orig_text, skip_style_tags=True)
    nym = NymSection(wiki, parent=None)
    assert str(nym) == orig_text

    senses = nym.filter_senses(recursive=False)
    assert len(senses) == 5

def test_complex_multiline():
    orig_text="""\
====Synonyms====
* {{sense|sense1}}
*: {{l|es|a}}
*: {{l|es|b}}
*: {{l|es|c}}
* {{sense|sense2}}
*: {{l|es|d}}
*: {{l|es|e}}
*: {{l|es|f}}
"""

    wiki = parse(orig_text, skip_style_tags=True)
    nym = NymSection(wiki, parent=None)
    assert str(nym) == orig_text

    senses = nym.filter_senses(recursive=False)
    assert len(senses) == 2
    sense = senses[0]
    assert sense.sense == "sense1"
    sense = senses[1]
    assert sense.sense == "sense2"

