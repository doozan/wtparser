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

import re

from ..wtnodes import WiktionaryNode
from ..utils import parse_anything, template_aware_splitlines

def get_section_type(title, default):

    from .pos import PosSection
    from .language import LanguageSection
    from .nym import NymSection
    from .etymology import EtymologySection
    from .usage import UsageSection

    for section in [ LanguageSection, PosSection, NymSection, EtymologySection, UsageSection ]:
        if section.matches_title(title):
            return section
    return default


def get_section_title(section):
    heading = next(iter(section.filter_headings(recursive=False)))
    return heading.strip("=").strip()


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
            self.heading = next(wikt.ifilter_headings(recursive=False))
            self._level = int(self.heading.count("=") / 2)
            self._name = self.heading.strip("=").strip()

        #        self._logname = parent._logname+"."+self._name if parent else self._name
        #        self.log = logging.getLogger(self._logname)

        # Parse sections will remove processed sections from wiki, so all that's left is data to be processed
        if parse_sections:
            self._parse_sections(wikt, section_handler)

        if parse_data:
            self._parse_data(wikt)

    @classmethod
    def matches_title(cls, title):
        """ Returns True if title matches a section this class can handle """
        raise ValueError("Classes must override this")

    def _parse_data(self, wikt):

        old_children = self._children
        self._children = []
        self._parse_list(str(wikt))
        self._children += old_children

    def _parse_sections(self, wikt, section_handler=None):
        for section in wikt.get_child_sections(self._level):
            nodes = wikt._pop_section(section)
            self.add_section(parse_anything(nodes), section_handler)

    def add_section(self, section, section_handler=None):
        from .unknown import UnknownSection

        title = get_section_title(section)
        section_type = (
            section_handler
            if section_handler
            else get_section_type(title, UnknownSection)
        )

        item = section_type(section, parent=self)
        if self._expected_sections is not None and title not in self._expected_sections:
            self.flag_problem("unexpected_section", title)

        self._children.append(parse_anything(item))

        if title in self._sections:
            self.flag_problem("duplicate_section", title)
        self._sections[title] = self._sections.get(title, []) + [item]


    def raise_subsections(self):

        if not self._parent:
            raise ValueError("No parent to move subsections to")

        # Everything after the first WiktionarySection is subsection stuff
        # that should be re-parented
        found = False
        for i, child in enumerate(self._children):
            for node in child.nodes:
                if isinstance(node, WiktionarySection):
                    found=True
                    break
            if found:
                break
        if not found:
            raise ValueError("no subsections found")

        new_parent = self._parent
        new_children = self._children[i:]
        for child in reversed(new_children):
            # TODO: Change header level on item and sub-items
            if hasattr(child, "_level"):
                child._level = self._level
            child._parent = new_parent
            new_parent.insert_after(self, child)
