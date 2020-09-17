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

__all__ = ["WTcode"]

from mwparserfromhell.wikicode import Wikicode


class WTcode(Wikicode):
    def __init__(self, wiki):
        self.nodes = wiki.nodes

    def _pop_section(self, section):
        index = self.index(section.nodes[0])
        count = len(section.nodes)

        nodes = []
        for x in range(count):
            node = self.nodes.pop(index)
            nodes.append(node)

        return nodes

    def _pop_data(self):
        """
        Pop all nodes before the first WiktionarySection
        """

        # the last items in self.nodes will always be WiktionarySections
        # NOTE: there may be some [[Category]] items after the sections
        # This could be optimized to search in reverse, since there are probably
        # fewer sections than there are other nodes
        from wtparser.wtnodes import WiktionarySection

        orig_len = len(self.nodes)
        nodes = []
        while len(self.nodes) and not isinstance(self.nodes[0], WiktionarySection):
            nodes.append(self.nodes.pop(0))

        return nodes

    def get_child_sections(self, start_level):
        """
        Returns a list of all direct child sections
        This is different than just calling get_sections(self._level+1),
        because this will find sections with even if they're deeper than level+1
        """
        child_sections = []
        all_sections = self.get_sections(include_lead=False)

        top_level = 0
        for section in all_sections:
            heading = next(section.ifilter_headings(recursive=False))
            if not start_level:
                start_level = heading.level
                continue

            if heading.level <= start_level:
                continue

            if not top_level:
                top_level = heading.level
            if heading.level <= top_level:
                top_level = heading.level
                child_sections.append(section)

        return child_sections



from .sections import WiktionarySection
from .sections.language import LanguageSection
from .sections.pos import PosSection
from .sections.nym import NymSection

from .wtnodes.word import Word
from .wtnodes.wordsense import WordSense
from .wtnodes.defitem import DefinitionItem
from .wtnodes.nymline import NymLine
from .wtnodes.nymsense import NymSense
from .wtnodes.decoratedlink import DecoratedLink

WTcode._build_filter_methods(
    sections=WiktionarySection,
    languages=LanguageSection,
    pos=PosSection,
    words=Word,
    wordsenses=WordSense,
    defitems=DefinitionItem,
    nymlines=NymLine,
    nyms=NymSection,
    nymsenses=NymSense,
    decoratedlinks=DecoratedLink,
)
