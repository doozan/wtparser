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
from ..utils import parse_anything

class Gloss(WiktionaryNode):
    """Handles gloss lines:
    # {{lb|es|Spain}} to [[run]]
    """

    @staticmethod
    def get_label_qualifiers(template):
        qualifiers = [ str(p) for p in template.params if p.name != "1" and str(p.name).isdigit() ]
        if "sort" in template.params:
            qualifiers = sorted(qualifiers)
        return qualifiers

    def handle_leading_anchors(self, text):
        templates = [ "anchor", "s", "senseid" ]
        re_templates = "|".join(templates)
        while re.match(r'\s*{{\s*(' + re_templates + ')\s*\|', text):
            wikt = parse_anything(text)
            template = next(wikt.ifilter_templates(recursive=False, matches=lambda x: x.name in templates))
            re_template = re.escape(str(template))
            text = re.sub(rf"^\s*{re_template}[:]?\s*", lambda x: self.add_text(x.group(0)), str(wikt))

        return text

    def handle_leading_labels(self, text):
        templates = ["label", "lb", "lbl", "indtr"]
        re_templates = "|".join(templates)
        while re.match(r'\s*{{\s*(' + re_templates + ')\s*\|', text):
            wikt = parse_anything(text)
            template = next(wikt.ifilter_templates(recursive=False, matches=lambda x: x.name in templates))

            self.qualifiers += self.get_label_qualifiers(template)

            re_template = re.escape(str(template))
            text = re.sub(rf"^\s*{re_template}[:,;]?\s*", lambda x: self.add_text(x.group(0)), str(wikt))

        return text

    def _parse_data(self, text):
        self.qualifiers = []
        self.data = ""

        pattern = r"(?P<start>\s*\#+\s*)(?P<data>.*)"
        res = re.match(pattern, text, re.DOTALL)
        self.add_text(res.group('start'))
        data = self.handle_leading_anchors(res.group('data'))
        self.data = self.handle_leading_labels(data)
        self.add_text(self.data)
