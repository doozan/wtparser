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
from ..nymsense import NymSense

def test_simple():
    orig_text="""* {{sense|word}} {{l|es|otherword}}\n"""
    expected_text = "{{syn|es|otherword}}"
    expected_flags = []

    nymsense = NymSense(orig_text, name="1", parent=None)
    assert len(nymsense.filter_wordlinks()) == 1
    assert str(nymsense) == orig_text


def test_complex():
    line1="*{{sense|stingy}} {{l|es|tacaño|g=m}}, {{l|es|tacaña|g=f}}, {{l|es|pesetero|g=m}}, {{l|es|pesetera|g=f}}\n"
    line2="*{{sense|stingy}} {{l|es|hijo de puta|g=m}}, {{l|es|hija de puta|g=f}}\n"

    nymsense = NymSense(line1, name="1", parent=None)
    assert len(nymsense.filter_wordlinks()) == 4
    assert str(nymsense) == line1

    orig_text = "".join([line1, line2])
    nymsense = NymSense(orig_text, name="1", parent=None)
    assert len(nymsense.filter_wordlinks()) == 6
    assert str(nymsense) == orig_text


def test_qualifiers():
    orig_text="* {{l|es|word1}} {{qualifier|q1, q2}}\n"
    nymsense = NymSense(orig_text, name="1", parent=None)

    assert str(nymsense) == orig_text
