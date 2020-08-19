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
from ..nymsection import NymSection

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
