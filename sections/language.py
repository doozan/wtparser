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

        # TODO: Fix this mess
        self._parent = parent
        heading = next(iter(wikt.filter_headings(recursive=False)))
        lang = heading.strip("=")
        if lang not in ALL_LANGUAGES:
            self.flag_problem("unknown_language", lang)
            self._lang_id = "ERROR_NOLANG"
        else:
            self._lang_id = ALL_LANGUAGES[lang]

        super().__init__(wikt, parent)
