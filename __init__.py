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
This will parse a section containing a wiktionary word
Currently handles word definition and nym sections
"""

__author__ = "Jeff Doozan"
__copyright__ = "Copyright (C) 2020 Jeff Doozan"
__license__ = "GPL3"
__version__ = "0.1.0"
__email__ = "wiktionary@doozan.com"

from . import (wtnodes, sections, utils, wtcode)

parse = utils.parse_anything

def parse_as(target, text, parent, **kwargs):
    return target(parse(text, **kwargs), parent=parent)

def parse_page(text, title, parent, **kwargs):
    from .sections.page import Page
    return Page(parse(text, **kwargs), name=title, parent=parent)

def parse_language(text, parent=None, **kwargs):
    from .sections.language import LanguageSection
    return parse_as(LanguageSection, text, parent=parent, **kwargs)
