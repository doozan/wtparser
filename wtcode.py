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
        from wtparser.nodes import WiktionarySection

        idx = 0
        for v in self.nodes:
            if isinstance(v, WiktionarySection):
                break
            idx += 1

        nodes = []
        for x in range(idx):
            nodes.append(self.nodes.pop(0))

        return nodes


# from .nodes.page import Page
from .nodes import WiktionarySection
from .nodes.language import LanguageSection
from .nodes.word import WordSection
from .nodes.definition import Definition
from .nodes.defitem import DefinitionItem
from .nodes.nymline import NymLine
from .nodes.nymsection import NymSection
from .nodes.nymsense import NymSense
from .nodes.wordlink import WordLink

WTcode._build_filter_methods(
    sections=WiktionarySection,
    languages=LanguageSection,
    words=WordSection,
    defs=Definition,
    defitems=DefinitionItem,
    nymlines=NymLine,
    nyms=NymSection,
    senses=NymSense,
    wordlinks=WordLink,
)
