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
from ..languages.all_ids import ALL_LANGS

from importlib import import_module

class LanguageSection(WiktionarySection):
    def __init__(self, wikt, parent):

        # Set self._lang_id before processing anything else so child sections can
        # query for it as needed during their creation
        heading = next(iter(wikt.filter_headings(recursive=False)))
        lang = heading.strip("=").strip()
        if lang not in ALL_LANGS:
            self._parent = parent
            self.flag_problem("unknown_language", lang)
            self._lang_id = "ERROR_NOLANG"
            self._lang = None
        else:
            lang_id = ALL_LANGS[lang]
            self._lang_id = lang_id

            # Each language can have a config file in languages/id with configuration
            # and functions for parsing language-specific templates
            try:
                self._lang = import_module(f".languages.{lang_id}", "enwiktionary_parser").Data
            except ModuleNotFoundError:
                pass

        super().__init__(wikt, parent)

    @classmethod
    def matches_title(cls, title):
        """ Returns True if title matches a section this class can handle """
        return title.strip() in ALL_LANGS

