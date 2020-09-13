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

from ..decoratedlink import DecoratedLink

def test_decoratedlink():
    decoratedlink = DecoratedLink("{{l|es|gabacho}} {{qualifier|Spain, Mexico}}", name="1", parent=None)
    assert decoratedlink.item == { "target": "gabacho", "q": "Spain, Mexico" }

    decoratedlink = DecoratedLink("word (qualifier)", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "q": "qualifier" }

    decoratedlink = DecoratedLink("[[word]] (qualifier)", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "q": "qualifier" }

    decoratedlink = DecoratedLink("[[word]] of [[words]] (qualifier)", name="1", parent=None)
    assert decoratedlink.item == { "target": "word of words", "q": "qualifier" }

    decoratedlink = DecoratedLink("word {{q|q1, q2}} (q3)", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "q": "q1, q2, q3" }
    # TODO: Check for duplicate sources flag

    decoratedlink = DecoratedLink(" {{l|es|frío}} {{g|m}} (Cuba, colloquial) ", name="1", parent=None)
    assert decoratedlink.item == { "target": "frío", "q": "Cuba, colloquial" }

    decoratedlink = DecoratedLink("[[word|altword]]", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "alt": "altword" }

    decoratedlink = DecoratedLink("[[word]]ness", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "alt": "wordness" }

    decoratedlink = DecoratedLink(" [[word|altword]] (blah)", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "alt": "altword", "q": "blah" }

    #decoratedlink = DecoratedLink(" [[nym5|more stuff]] (blah5) ", name="1", parent=None)
    #assert decoratedlink.item == { "target": "nym5", "alt": "mare stuff", "gloss": "blah5" }

    decoratedlink = DecoratedLink(" ''(qualifier)'' {{l|es|word}} ", name="1", parent=None)
    assert decoratedlink.item == { "target": "word", "q": "qualifier" }

