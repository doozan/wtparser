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
from ..gloss import Gloss
from ...utils import parse_anything

def test_simple(word):
    text = "# {{lb|es|Mexico|slang}} {{lb|es|transitive}} to [[contribute]]; to [[bring]]."
    gloss = Gloss(text, name="1", parent=word)
    assert gloss.qualifiers == ["Mexico", "slang", "transitive"]
