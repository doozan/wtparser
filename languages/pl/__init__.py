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
Data and utilities for processing Polish sections of enwiktionary
"""

from .. import LanguageData

class Data(LanguageData):
    headwords = {
        "pl-adj",
        "pl-adv",
        "pl-noun",
        "pl-prep",
        "pl-proper noun",
        "pl-verb"
    }

    @classmethod
    def get_forms(cls, word):
        return {}

    @classmethod
    def get_form_sources(cls, word):
        template = word.headword
        if template is None:
            return []

        return [template]
