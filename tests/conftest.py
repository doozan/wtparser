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

class ErrorHandler():
    def __init__(self):
        self.problems = {}

    def flag_problem(self, problem, *data):
        self.problems[problem] = self.problems.get(problem, []) + [data]

    def clear_problems(self):
        self.problems = {}

@pytest.fixture()
def err():
    return ErrorHandler()

