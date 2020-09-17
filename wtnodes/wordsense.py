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

import re

from ..utils import parse_anything, get_template_depth, template_aware_splitlines
from ..constants import ALL_NYMS, NYM_ORDER, TAG_TO_NYM, ALL_NYM_TAGS
from . import WiktionaryNode
from .gloss import Gloss
from .nymline import NymLine


class WordSense(WiktionaryNode):
    def __init__(self, text, name, parent):
        self._lines = []

        self.sense_ids = []
        self.sense_labels = []
        self.sense_words = set()

        self.nymlines = {}
        super().__init__(text, name, parent)

    def _parse_data(self, text):
        self._children = []
        for line in template_aware_splitlines(text, True):
            self._parse_item(line)

    def _parse_item(self, line):

        if line.startswith("# ") or line.startswith("#{"):
            self.parse_hash(line)

        # Index any existing nym tags
        elif line.startswith("#:"):
            self.parse_hashcolon(line)

        elif line.startswith("#*"):
            self.parse_hashstar(line)

        elif line.startswith("##"):
            self.parse_hashhash(line)

        else:
            if line.strip() != "":
                self.flag_problem("unexpected_text", line)
            self.parse_unhandled(line)

    def add_gloss(self, line):
        item = Gloss(line, name=len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))
        return item

    def add_defitem(self, line):
        item = WiktionaryNode(line, name=len(self._children) + 1, parent=self)
        self._children.append(parse_anything(item))
        return item

    def add_nymline(self, line, smart_position=False, no_merge=False):
        """
        Add a nymline to the definition
        If smart_position is True, insert at the 'correct' position
        Otherwise, append to the end of the definition
        If no_merge is True, creates a new entry line, even if a line
        of the same type already exists, and prevents future additions
        from being merged into the new entry
        """
        res = re.match(r"#:\s*{{(" + "|".join(ALL_NYM_TAGS) + r")\|[^{}]+}}", line)
        if not res:
            self.flag_problem("nymline_missing_syn_tag", line)
            return

        nymline = NymLine(line, name=len(self._children) + 1, parent=self)

        nym_type = TAG_TO_NYM[res.group(1)]
        if self.has_nym(nym_type) and not no_merge and not "FIXME" in str(self.get_nym(nym_type)):
            self.flag_problem("duplicate_nyms", line)
            orig_nymline = self.get_nym(nym_type)
            orig_nymline.add_nymline(nymline)
        else:
            if smart_position:
                index = self.get_nym_target(nym_type)
                self._children.insert(index, parse_anything(nymline))
            else:
                self._children.append(parse_anything(nymline))
            self.nymlines[nym_type] = nymline

    def parse_unhandled(self, line):
        self._children.append(parse_anything(line, skip_style_tags=True))

    def parse_hash(self, line):
        self.add_sense_words(line[1:])

        wikt = parse_anything(line, skip_style_tags=True)
        self.add_sense_labels(
            wikt.filter_templates(
                recursive=False, matches=lambda x: x.name in ["lb", "lbl", "label"]
            )
        )
        self.add_sense_ids(
            wikt.filter_templates(
                recursive=False, matches=lambda x: x.name == "senseid"
            )
        )

        self.add_gloss(line)

    def parse_hashcolon(self, line):
        res = re.match(r"#:\s*{{(" + "|".join(ALL_NYM_TAGS) + r")\|[^{}]+}}", line,)
        if res:
            self.add_nymline(line)
            return

        # TODO: Handle other stuff
        # #: {{ux|es|'''Me puse''' las gafas.|translation=I put my glasses on.}}\n",

#        self.flag_problem("hashcolon_is_not_nym", line)
        self.add_defitem(line)

    def parse_hashstar(self, line):
        return self.add_defitem(line)

    def parse_hashhash(self, line):
        return self.add_defitem(line)

    def has_nym(self, nym_name):
        # assert nym_name in ALL_NYMS
        return nym_name in self.nymlines

    def get_nym(self, nym_name):
        return self.nymlines.get(nym_name, None)

    def get_nym_target(self, nym_title):
        """
        Return the _children index for the nymline to be inserted
        """
        max_order = NYM_ORDER.index(nym_title)

#        if nym_title in self.nymlines:
#            raise ValueError("already exists")

        after_idx = -1
        after = None
        first_idx = 999
        first = None
        for nym_name, obj in self.nymlines.items():
            idx = NYM_ORDER.index(nym_name)
            if idx < first_idx:
                first_idx = idx
                first = obj

            if idx > max_order:
                continue

            if idx > after_idx:
                after = obj
                after_idx = idx

        if after:
            for i, child in enumerate(self._children):
                for node in child.nodes:
                    if node is obj:
                        return i+1

        # If no target was found to insert the object after,
        # insert it before the first nym or, if no nyms,
        # append it to the very end
        if first:
            for i, child in enumerate(self._children):
                for node in child.nodes:
                    if node is obj:
                        return i

        return len(self._children)

    def has_sense(self, sense):
        for sense in re.split(r'[\W_]+', sense):
            if (
                sense != "" and
                sense not in self.sense_ids
                and sense not in self.sense_labels
                and sense not in self.sense_words
            ):
                return False
        return True

    def has_sense_id(self, sense):
        for sense in re.split(r'[\W_]+', sense):
            if not sense in self.sense_ids:
                return False
        return True

    def has_sense_label(self, sense):
        for sense in re.split(r'[\W_]+', sense):
            if not sense in self.sense_labels:
                return False
        return True

    def has_sense_word(self, sense):
        for sense in re.split(r'[\W_]+', sense):
            if not sense in self.sense_words:
                return False
        return True

    def add_sense_words(self, line):
        stripped = re.sub(r'(\[\[|\]\])', '', line)
        stripped = re.sub(r'[\W_]+', ' ', stripped)
        self.sense_words |= set(stripped.split(' '))
        if "" in self.sense_words:
            self.sense_words.remove("")

    def add_sense_labels(self, templates):
        if not templates:
            return

        if len(templates) > 1:
            self.flag_problem("multiple_sense_labels", templates)

        for template in templates:
            if template.get("1") != self.lang_id:
                self.flag_problem("sense_label_lang_mismatch", self.lang_id, template)

            self.sense_labels += [
                str(p.value)
                for p in template.params
                if p.name.isdigit and int(str(p.name)) > 1
            ]

    def add_sense_ids(self, templates):
        if not templates:
            return

        if len(templates) > 1:
            self.flag_problem("multiple_senseids", templates)

        for template in templates:
            if template.get("1") != self.lang_id:
                self.flag_problem("senseid_lang_mismatch", self.lang_id, template)

            value = str(template.get("2"))
            if not value:
                self.flag_problem("senseid_no_value", template)
            else:
                self.sense_ids.append(str(template.get("2")))
