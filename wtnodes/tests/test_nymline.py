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

from ..nymline import NymLine

def test_from_nymsense(nymsense):
    nymline = NymLine.from_nymsense(nymsense, name="1", parent=None)
    assert nymline == "#: {{syn|es|nounsyn1|q1=blah1|nounsyn2|q2=blah2}}\n"

def test_nymline():
    nymline = NymLine("* {{syn|es|syn1|alt1=alter1|syn2|q2=qual2|tr2=tran2}}\n", name="1", parent=None)
    items = nymline.items
    assert len(items) == 2

    item = items[0]
    assert item["target"] == "syn1"
    assert item["alt"] == "alter1"
    assert "q" not in item

    item = items[1]
    assert item["target"] == "syn2"
    assert item["q"] == "qual2"
    assert item["tr"] == "tran2"

    assert items == [{'target': 'syn1', 'alt': 'alter1'}, {'target': 'syn2', 'tr': 'tran2', 'q': 'qual2'}]

    new_nymline = NymLine("* {{syn|es|syn3|alt1=alter3|q1=qual3|tr1=tran3}}\n", name="2", parent=None)
    newitem = new_nymline.items[0]
    nymline.add(newitem)
    assert nymline == "* {{syn|es|syn1|alt1=alter1|syn2|tr2=tran2|q2=qual2|syn3|alt3=alter3|tr3=tran3|q3=qual3}}\n"

    nymline = NymLine("* {{syn|es|syn|syn2|Thesaurus:word}}\n", name="2", parent=None)
    nymline.add(newitem)
    assert nymline == "* {{syn|es|syn|syn2|syn3|alt3=alter3|tr3=tran3|q3=qual3|Thesaurus:word}}\n"

    # inline modifiers
    nymline = NymLine("* {{syn|es|syn1<alt:alter1>|syn2<q:qual2><tr:tran2>}}\n", name="1", parent=None)
    items = nymline.items
    assert items == [{'target': 'syn1', 'alt': 'alter1'}, {'target': 'syn2', 'tr': 'tran2', 'q': 'qual2'}]
