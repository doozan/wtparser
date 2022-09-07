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
This handles lines in definitions
"""

import re
from . import WiktionaryNode
from ..utils import parse_anything, get_label_qualifiers

class Gloss(WiktionaryNode):
    """Handles gloss lines:
    # {{lb|es|Spain}} to [[run]]
    """

    @staticmethod
    def get_indtr_qualifiers(t):
        types = {
            "intr": "intransitive",
            "ditr": "ditransitive",
            "cop": "copulative",
            "aux": "auxiliary",
        }
        q = [ str(v) for k,v in types.items() if t.has(k) ]
        if not q:
            q = [ "transitive" ]

        return q

    _anchors = { "anchor", "s", "senseid" }
    _labels = { "label", "lb", "lbl", "term-label" }
    _indtr = { "indtr" }
    _categories = { "c", "C", "cat", "top", "topic", "topics", "categorize", "catlangname", "catlangcode", "cln", "DEFAULTSORT" }
    _all_leading_templates = _anchors | _labels | _indtr | _categories

    def consume_leading_templates(self, text):
        """Process leading anchor and label templates

        Returns remainder of line"""

        re_templates = "|".join(map(re.escape, self._all_leading_templates))
        while re.match(r'\s*{{\s*(' + re_templates + r')\s*\|', text):
            wikt = parse_anything(text)
            template = next(wikt.ifilter_templates(recursive=False), None)
            if template is None:
                break

            if template.name.strip() in self._labels:
                self.qualifiers += get_label_qualifiers(template)

            # Scrape basic verb qualifiers from indtr, but don't parse/strip them
            elif template.name.strip() in self._indtr:
                self.qualifiers += self.get_indtr_qualifiers(template)
                return text

            re_template = re.escape(str(template))
            text = re.sub(rf"^\s*{re_template}[:]?\s*", lambda x: self.add_text(x.group(0)), str(wikt))

        return text

    def _parse_data(self, text):
        self.qualifiers = []
        self.data = ""

        pattern = r"(?P<start>\s*\#+\s*)(?P<data>.*)"
        res = re.match(pattern, text, re.DOTALL)
        self.add_text(res.group('start'))
        self.data = self.consume_leading_templates(res.group('data'))
        self.add_text(self.data)
