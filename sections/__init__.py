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

# import logging
import re
from itertools import chain

from ..nodes import WiktionaryNode
from ..utils import parse_anything, template_aware_splitlines

def get_section_type(title, default):

    from ..constants import ALL_LANGUAGES, ALL_POS, ALL_NYMS
    from .word import WordSection
    from .language import LanguageSection
    from .nymsection import NymSection

    if title in ALL_LANGUAGES:
        return LanguageSection
    elif title in ALL_POS:
        return WordSection
    elif title in ALL_NYMS:
        return NymSection
    else:
        return default
    return default


def get_section_title(section):
    heading = next(iter(section.filter_headings(recursive=False)))
    return heading.strip("=")


class WiktionarySection(WiktionaryNode):
    def __init__(
        self,
        wikt,
        parent=None,
        parse_header=True,
        parse_sections=True,
        section_handler=None,
        parse_data=True
    ):
        self._parent = parent

        self._children = []
        self._sections = {}

        if not hasattr(self, "_expected_sections"):
            self._expected_sections = None

        if parse_header:
            self.heading = next(iter(wikt.filter_headings(recursive=False)))
            self._level = int(self.heading.count("=") / 2)
            self._name = self.heading.strip("=")

        #        self._logname = parent._logname+"."+self._name if parent else self._name
        #        self.log = logging.getLogger(self._logname)

        # Parse sections will remove processed sections from wiki, so all that's left is data to be processed
        if parse_sections:
            self._parse_sections(wikt, section_handler)

        if parse_data:
            self._parse_data(wikt)

    def _prepare_line(self, line):
        """Hook to modify line before it's passed to the parser"""
        return line

    def _parse_data(self, wikt):
        """
        Generic line-by-line parser
        """

        section_text = str(wikt)
        old_children = self._children
        self._children = []

        current_item = []
        unhandled = []

        in_header = True
        in_footer = False
        self._heading_found = False

        for line in template_aware_splitlines(section_text, True):
            line = self._prepare_line(line)

            in_header = self._is_header(line) if in_header else False

            if in_header or in_footer:
                unhandled.append(line)

            elif re.match(r"\s+$", line):
                if current_item:
                    current_item.append(line)
                else:
                    unhandled.append(line)

            elif current_item and self._is_still_item(line):
                current_item.append(line)

            elif self._is_new_item(line):
                if len(unhandled):
                    self.add_text(unhandled)
                    unhandled = []

                if len(current_item):
                    self.add_item(current_item)
                    current_item = []

                current_item.append(line)

            elif self._is_footer(line):
                in_footer=True
                unhandled.append(line)

            # Unexpected text
            else:
                if current_item:
                    self.add_item(current_item)
                    current_item = []

                if not self._handle_other(line):
                    unhandled.append(line)

        if current_item:
            self.add_item(current_item)
            current_item = []
        elif len(unhandled):
            self.add_text(unhandled)
            unparsed = []

        self._children += old_children

    def _is_header(self, line):

        if re.match(r"\s+$", line):
            return True

        if not self._heading_found and re.match(r"\s*==", line):
            self._heading_found=True
            return True

        return False


    def _is_footer(self, line):

        re_endings = [ r"\[\[\s*Category\s*:" r"==[^=]+==", r"----" ]
        template_endings = [ "c", "C", "top", "topics", "categorize", "catlangname", "catlangcode", "cln", "DEFAULTSORT" ]
        re_endings += [ r"\{\{\s*"+item+r"\s*\|" for item in template_endings ]
        endings = "|".join(re_endings)

        if re.match(fr"\s*({endings})", line):
            return True
        return False

    def _is_new_item(self, line):
        return False

    def _is_still_item(self, line):
        return False

    def _handle_other(self, line):
        self.flag_problem("unhandled_line", line)
        return False

#    def _parse_sections(self, wikt, section_handler=None):
#
#        sections = []
#        for section in reversed(self.get_child_sections(wikt)):
#            title = get_section_title(section)
#            nodes = wikt._pop_section(section)
#            sections.insert(0, (title, parse_anything(nodes)))
#
#        # add parsed objects back to smartlist
#        for title, section in sections:
#            section_type = (
#                section_handler
#                if section_handler
#                else get_section_type(title, WiktionarySection)
#            )
#            item = section_type(section, parent=self)
#            if self._expected_sections is not None and title not in self._expected_sections:
#                self.flag_problem("unexpected_section", title)
#
#            self._children.append(parse_anything(item))
#
#            if title in self._sections:
#                self.flag_problem("duplicate_section", title)
#            self._sections[title] = self._sections.get(title, []) + [item]

    def _parse_sections(self, wikt, section_handler=None):
        for section in wikt.get_child_sections(self._level):
            nodes = wikt._pop_section(section)
            self.add_section(parse_anything(nodes), section_handler)

    def add_section(self, section, section_handler=None):
        title = get_section_title(section)
        section_type = (
            section_handler
            if section_handler
            else get_section_type(title, WiktionarySection)
        )

        item = section_type(section, parent=self)
        if self._expected_sections is not None and title not in self._expected_sections:
            self.flag_problem("unexpected_section", title)

        self._children.append(parse_anything(item))

        if title in self._sections:
            self.flag_problem("duplicate_section", title)
        self._sections[title] = self._sections.get(title, []) + [item]
