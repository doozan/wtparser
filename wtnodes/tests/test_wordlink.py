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

from ..wordlink import WordLink

def test_wordlink():
    wordlink = WordLink("{{l|es|gabacho}} {{qualifier|Spain, Mexico}}", name="1", parent=None)
    assert wordlink.item == { "target": "gabacho", "q": "Spain, Mexico" }

    wordlink = WordLink("word (qualifier)", name="1", parent=None)
    assert wordlink.item == { "target": "word", "q": "qualifier" }

    wordlink = WordLink("[[word]] (qualifier)", name="1", parent=None)
    assert wordlink.item == { "target": "word", "q": "qualifier" }

    wordlink = WordLink("[[word]] of [[words]] (qualifier)", name="1", parent=None)
    assert wordlink.item == { "target": "word of words", "q": "qualifier" }

    wordlink = WordLink("word {{q|q1, q2}} (q3)", name="1", parent=None)
    assert wordlink.item == { "target": "word", "q": "q1, q2, q3" }
    # TODO: Check for duplicate sources flag

    wordlink = WordLink("{{l|es|frío}} {{g|m}} (Cuba, colloquial)", name="1", parent=None)
    assert wordlink.item == { "target": "frío", "q": "Cuba, colloquial" }
