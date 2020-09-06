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

def test_errors(page, language, nymsection, nymline):

    assert page.problems == {}

    language.flag_problem("lang")
    assert "lang" in page.problems.keys()

    nymsection.flag_problem("nym")
    assert "nym" in page.problems.keys()

    nymline.flag_problem("nymline")
    assert "nymline" in page.problems.keys()


