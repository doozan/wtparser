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
This will parse a section containing a etymology
"""

from . import WiktionarySection

class EtymologySection(WiktionarySection):
    """ Parses an Etymology section into text
    ===Etymology===
    From {{inh|es|la|tabula}}.
    """

    @classmethod
    def matches_title(cls, title):
        """ Returns True if title matches a section this class can handle """
        return title.lower().strip() == "etymology"
