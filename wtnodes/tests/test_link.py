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

from ..link import Link

def test_link():
    link = Link("{{l|es|word}}", name="1", parent=None)
    assert link.target == "word"

    link = Link(" {{l|es|word}} ", name="1", parent=None)
    assert link.target == "word"

    link = Link(" {{l|es|word1}} {{l|es|word2}} ", name="1", parent=None)
    assert link.target == "word1 word2"

    link = Link(" {{l|es|word}} of {{l|es|words}} ", name="1", parent=None)
    assert link.target == "word of words"

    link = Link(" [[word]] ", name="1", parent=None)
    assert link.target == "word"

    link = Link("[[word]]", name="1", parent=None)
    assert link.target == "word"

    link = Link("[[word]] of [[words]]", name="1", parent=None)
    assert link.target == "word of words"

    link = Link("word", name="1", parent=None)
    assert link.target == "word"

    link = Link("[[word|altword]]", name="1", parent=None)
    assert link.target == "word"
    assert link.alt == "altword"

    link = Link("[[word]]ness", name="1", parent=None)
    assert link.target
    assert link.alt == "wordness"

    # Ignore "pipe trick"
    link = Link(" [[word|]] ", name="1", parent=None)
    assert link.target == "word"
    assert link.alt is None

