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
from ..wordsense import WordSense
from ..nymsense import NymSense
from ...sections.nym import NymSection
from ...utils import parse_anything

def test_wordsense(word):

    d = WordSense("# {{senseid|es|blah}} [[word1]], [[word3]], [[word2]]", name="test", parent=word)
    assert d.has_nym("Synonyms") == False
    #assert d.is_good() == True
    assert d.sense_ids == ["blah"]
    assert d.sense_labels == []

    syn_section = NymSection(parse_anything("===Synonyms===\n* {{l|es|syn1}}\n"), parent=word)
#    d.add_nymsense(syn_section.filter_nymsenses()[0])
#    assert d.has_nym("Synonyms") == True
    #assert d.is_good() == True

#    assert d.has_nym("Antonyms") == False
#    syn_section = NymSection(parse_anything("===Antonyms===\n* {{l|es|ant1}}\n"), parent=word)
#    d.add_nymsense(syn_section.filter_nymsenses()[0])
#    assert d.has_nym("Antonyms") == True
    #assert d.is_good() == True

#    d.add("#: {{synonyms|es|word3}}")
#    assert d.has_nym("Synonyms") == True
    # TODO: error handling
#    assert d.is_good() == False
#    assert sorted(d._err.errors.keys()) == sorted(["duplicate_nyms"])

    #err.clear()
    #d = WordSense("# [[word]]")
    #d.add("#: {{unknown|es|word3}}")
    #assert sorted(err.errors.keys()) == sorted(["def_hashcolon_is_not_nym"])

    # TODO: Check nym language matches lang_id
    # Nym lines are currently not parsed beyond getting the template name
    #    d = WordSense("es", "# [[word]]")
    #    d.add("#: {{ant|en|word2}}")
    #    assert sorted([ k for k,v in d.get_problems() ]) == sorted([ "nym_language_mismatch" ])

    #err.clear()
    d = WordSense("# {{senseid|es|word}} [[word]] (qualifier)", name="test", parent=word)
    assert d.sense_ids == ["word"]
    #assert sorted(err.errors.keys()) == sorted([])

    #err.clear()
    d = WordSense("# {{senseid|en|word}} [[word]] (qualifier)", name="test", parent=word)
    assert d.sense_ids == ["word"]
    #assert sorted(err.errors.keys()) == sorted(["def_senseid_lang_mismatch"])


def test_senes(word):
    d = WordSense("# {{senseid|es|sense1}} [[word1]]", name="test", parent=word)
    assert d.sense_ids == ["sense1"]
    assert d.sense_labels == []

    # sense =  "s1|s2"

def test_nymline_syn(word):
    text = """\
# [[word]]
#: {{syn|syn1}}
"""

    d = WordSense(text, name="test", parent=word)
    nymlines = d.filter_nymlines()
    assert len(nymlines) == 1
    assert nymlines[0] == "#: {{syn|syn1}}\n"

def test_nymline_synonyms(word):
    text = """\
# [[word]]
#: {{synonyms|syn1}}
"""

    d = WordSense(text, name="test", parent=word)
    nymlines = d.filter_nymlines()
    assert len(nymlines) == 1
    assert nymlines[0] == "#: {{synonyms|syn1}}\n"


def xtest_insert_nym_after(word):

    defstr = """# [[word]], [[word2]]; [[word3]]
## stuff
##: more stuff"""
    syn = "#: {{syn|es|syn1}}\n"
    ant = "#: {{ant|es|ant1}}\n"

    d = WordSense(defstr, name="test", parent=word)
    assert str(d) == defstr

    assert d.has_nym("Antonyms") == False
    syn_section = NymSection(parse_anything("===Antonyms===\n* {{l|es|ant1}}\n"), parent=word)
    d.add_nymsense(syn_section.filter_nymsenses()[0])
    assert "".join([defstr, ant]) == str(d)

    syn_section = NymSection(parse_anything("===Synonyms===\n* {{l|es|syn1}}\n"), parent=word)
    d.add_nymsense(syn_section.filter_nymsenses()[0])
    # Synonyms should be positioned above Antonyms
    assert "".join([defstr, syn, ant]) == str(d)


def xtest_insert_nym_middle(word):
    defstr = "# [[word]], [[word2]]; [[word3]]\n"
    syn = "#: {{syn|es|syn1}}\n"
    extra = "## stuff\n##: more stuff\n"
    ant = "#: {{ant|es|ant1}}\n"

    d = WordSense("".join([defstr,syn,extra]), name="test", parent=word)
    assert str(d) == "".join([defstr,syn,extra])

    assert d.has_nym("Antonyms") == False
    syn_section = NymSection(parse_anything("===Antonyms===\n* {{l|es|ant1}}\n"), parent=word)
    d.add_nymsense(syn_section.filter_nymsenses()[0])
    assert str(d) == "".join([defstr,syn,ant,extra])


def xtest_insert_nym_add(nymsense,nymsection,word):
    defstr = "# [[word]], [[word2]]; [[word3]]\n"

    d = WordSense(defstr, name="test", parent=word)
    d.add_nymsense(nymsense)
    expected_syn = "#: {{syn|es|nounsyn1|q1=blah1|nounsyn2|q2=blah2}}\n"
    assert "".join([defstr, expected_syn]) == str(d)

    orig_text="* {{l|es|anotherword}}\n"
    new_nymsense = NymSense(orig_text, name="1", parent=nymsection)
    d.add_nymsense(new_nymsense)
    expected_syn = "#: {{syn|es|nounsyn1|q1=blah1|nounsyn2|q2=blah2|anotherword}}\n"
    assert "".join([defstr, expected_syn]) == str(d)




def xtest_add_existing_nymsense(nymsection,word):

    defstr = "# a [[word]], a [[word2]]; [[word3]]\n#: {{syn|es|syn1}}\n"

    d = WordSense(defstr, name="test", parent=word)

    sense2 = NymSense("* {{sense|nomatch2}} {{l|es|syn2}}\n", name="2", parent=nymsection)

    d.add_nymsense(sense2)
    assert d == "# a [[word]], a [[word2]]; [[word3]]\n#: {{syn|es|syn1|syn2}}\n"

def xtest_add_existing_nymsense_nomatch(nymsection,word):

    defstr = "# a [[word]], a [[word2]]; [[word3]]\n#: {{syn|es|syn1}}\n"

    d = WordSense(defstr, name="test", parent=word)

    sense2 = NymSense("* {{sense|nomatch2}} {{l|es|syn2}}\n", name="2", parent=nymsection)

    d.add_nymsense(sense2, no_merge=True)
    assert d == "# a [[word]], a [[word2]]; [[word3]]\n#: {{syn|es|syn1}}\n#: {{syn|es|syn2}} <!-- FIXME, MATCH SENSE: 'nomatch2' -->\n"
