#
# from ..constants import SECTION_TYPES
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

import re

from . import WiktionarySection
from ..utils import parse_anything, template_aware_splitlines
from .definition import Definition
from .language import LanguageSection


class WordSection(WiktionarySection):
    def __init__(self, wikt, parent=None, lang_id=None):
        super().__init__(wikt, parent)

        self.lang_id = (
            lang_id if lang_id else self.get_ancestor_value("lang_id", "ERROR")
        )

        self._parse_data(wikt)

    def _parse_data(self, wikt):
        """
        Converts any line starting with "# " and any following "#[*]" lines into
        Definition nodes
        """

        data_nodes = wikt._pop_data()
        old_children = self._children
        self._children = []

        section_text = "".join(map(str, data_nodes))

        current_item = []
        unhandled = []

        in_header = True
        in_footer = False

        for unstripped_line in template_aware_splitlines(section_text, True):
            line = unstripped_line.strip()
            if in_footer:
                unhandled.append(unstripped_line)

            elif line == "":
                if current_item:
                    current_item.append(unstripped_line)
                else:
                    unhandled.append(unstripped_line)

            # Header is expected to look like
            # ===Section===
            #
            # {{es-noun}}
            #
            # # start of definitions
            elif in_header:
                unhandled.append(unstripped_line)
                # TODO: This should only find one header == line
                if line.startswith("=="):
                    continue

                # The header ends after declaring a word
                if line.startswith("{{" + self.lang_id + "-") or line.startswith(
                    "{{head"
                ):  # fix folding }}}}
                    in_header = False
                else:
                    self.flag_problem("text_before_header", line)

            elif line.startswith("# ") or line.startswith("#{"):
                if len(unhandled):
                    self.add_text(unhandled)
                    unhandled = []

                if len(current_item):
                    self.add_def(current_item)
                    current_item = []

                current_item.append(unstripped_line)

            elif current_item and line.startswith("#"):
                current_item.append(unstripped_line)

            # Start footer when we come to the end of the section or the Category declarations
            # or another section
            elif (
                line.startswith("----")
                or line.startswith("[[Category:")
                or line.startswith("==")
            ):
                in_footer = True
                unhandled.append(unstripped_line)

            # Word declaration
            elif line.startswith("{{" + self.lang_id + "-") or line.startswith(
                "{{head"
            ):  # fix folding }}}}

                # Some articles list multiple parts of speech or etymology without breaking them  into sections.
                # If we encounter a new declaration, flag it for manual review and stop processing
                self.flag_problem("multiple_word_declarations_in_def", line)
                if current_item:
                    self.add_def(current_item)
                    current_item = []

                in_footer = True
                unhandled.append(unstripped_line)

            # Unexpected text
            else:
                if current_item:
                    self.add_def(current_item)
                    current_item = []

                unhandled.append(unstripped_line)
                if in_header:
                    self.flag_problem("unexpected_text_before_def", line)
                else:
                    self.flag_problem("unexpected_text_after_def", line)

        if current_item:
            self.add_def(current_item)
            current_item = []
        elif len(unhandled):
            self.add_text(unhandled)
            unparsed = []

        self._children += old_children

    def add_def(self, lines):
        """
        Creates a new Definition from the supplied text
        Returns an array [ leading_newlines, Definition, trailing_newlines ]
        """
        self.add_text(self.pop_leading_newlines(lines))

        trailing_newlines = self.pop_trailing_newlines(lines)
        item = Definition("".join(lines), len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))

        self.add_text(trailing_newlines)

    def get_defs_matching_sense(self, nym_sense):
        return self.filter_defs(
            recursive=False, matches=lambda d: d.has_sense(nym_sense)
        )
