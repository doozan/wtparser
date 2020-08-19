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

"""
This will parse a section containing a wiktionary language
Currently handles words
"""

from . import WiktionarySection
from ..constants import ALL_LANGUAGES


class LanguageSection(WiktionarySection):
    def __init__(self, wikt, parent):
        super().__init__(wikt, parent, parse_sections=False)

        if self._name not in ALL_LANGUAGES:
            self.flag_problem("unknown_language", self._name)
            self.lang_id = "ERROR_NOLANG"
        else:
            self.lang_id = ALL_LANGUAGES[self._name]

        self._parse_sections(wikt)
