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
A Link to exactly one wiktionary page, including the link, qualifiers, and gloss
"""

# TODO Use Link as an object instead of a dict, move link setter to Link

import re

from . import WiktionaryNode
from ..utils import parse_anything
from .link import Link

class DecoratedLink(WiktionaryNode):
    def __init__(self, text, name, parent):
        self._has_changed = False

        self._text = text

        # Link is a dict containing, at mininum, "target" and, optionally, "tr" and "alt" values
        self._link = {}
        self.qualifiers = []
        self.gloss = []
        self.trailing = None

        super().__init__(text, name, parent)

    def __unicode__(self):
        if self._has_changed:
            results = []
            if self._link:
                results.append(self.get_formatted_link())
            if self.qualifiers:
                results.append(self.get_formatted_qualifiers())
            return " ".join(results)
        else:
            return self._text

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        if isinstance(value, str):
            if not "target" in self._link or self._link["target"] != value:
                self._has_changed = True
                self._link = {"target": value}

        elif self._link != value:
            self._has_changed = True
            self._link = value

    @property
    def item(self):
        res = dict(**self._link) if self._link else {}

        if self.qualifiers:
            if "q" in res:
                self.flag_problem("mulitple_q_values", self.qualifiers, res["q"])

                # merge both lists, stripping any duplicate values
                all_values = list(dict.fromkeys(res["q"] + self.qualifiers))
                res["q"] = ", ".join(all_values)
            else:
                res["q"] = ", ".join(self.qualifiers)

        if self.gloss:
            if "gloss" in res:
                self.flag_problem("mulitple_gloss_values", self.gloss, res["gloss"])

                # merge both lists, stripping any duplicate values
                all_gloss = list(dict.fromkeys(res["gloss"] + self.gloss))
                res["gloss"] = ", ".join(all_gloss)
            else:
                res["gloss"] = ", ".join(self.gloss)

        if "gloss" in res and '"' in res["gloss"]:
            self.flag_problem("autofix_gloss_has_quotes", res["gloss"])
            res["gloss"] = res["gloss"].strip('"')

        return res

    def get_formatted_link(self):
        if (
            not self._link
            or not "target" in self._link
            or not len(self._link["target"])
        ):
            return "{{l||ERROR}}"

        # TODO: Warn if there are other values in _link that are discarded
        params = [self.lang_id, self._link["target"]]
        params += [f"{k}={self._link[k]}" for k in ["alt", "tr"] if k in self._link]
        return "{{l|" + "|".join(params) + "}}"

    def get_formatted_qualifiers(self):
        if not self.qualifiers or not len(self.qualifiers):
            return None
        return "{{q|" + "|".join(self.qualifiers) + "}}"

    def _parse_data(self, text):
        """
        Parses a word defined with [[link]] or {{l}}, {{q}} or (qualifier) and {{gloss}} tags while ignoring {{g}} tags
        Flags an error if unexpected tags or text are found or if an item is defined twice
        """

        # Special handling for "See [[Thesaurus:entry]]." items
        res = re.match(r"(?:{{s(?:ense)?|[^}]+}})?(?:For more,)?\s*[sS]ee(?: also)? \[\[(Thesaurus:[^\]]+)\]\]\.?\s*$", text)
        if res:
            self._link = {"target": res.group(1)}
            return

        gloss, text = self.extract_gloss(text)
        qualifiers, text = self.extract_qualifiers(text)
        link = self.get_link(text)

        if not link or link == {}:
            self.flag_problem("missing_link", text)

        self._link = link
        self.qualifiers = qualifiers
        self.gloss = gloss

    def extract_templates_and_patterns(self, templates, patterns, text):

        response = {"templates": [], "patterns": [], "text": ""}

        wikt = parse_anything(text, skip_style_tags=True)

        for template in wikt.filter_templates(recursive=False):
            if template.name in templates:
                response["templates"].append(template)
                wikt.remove(template)

        text = str(wikt)
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if len(matches):
                response["patterns"].append(matches)
                text = re.sub(pattern, "", text)

        response["text"] = text
        return response

    def stripformat(self, text):

        text = text.strip()

        newtext = re.sub(r"^\[+(.*?)\]+$", r"\1", text)
        text = newtext.strip() if newtext else text

        newtext = re.sub(r"^'+(.*?)'+$", r"\1", text)
        text = newtext.strip() if newtext else text

        newtext = re.sub(r"^\"+(.*?)\"+$", r"\1", text)
        text = newtext.strip() if newtext else text

        return text.strip()

    def extract_qualifiers(self, text):
        pattern = r"""(?x)
        \'*         # formatting quotes
        \(          # opening (
        ([^)]*)     # contents
        \)          # closing )
        \'*         # formatting quotes
        """

        res = self.extract_templates_and_patterns(
            ["lb", "lbl", "label", "i", "q", "qual", "qualifier"], [pattern], text
        )
        q = []

        if len(res["templates"]) > 1:
            self.flag_problem("qualifier_multiple_templates")

        if len(res["patterns"]) > 1:
            self.flag_problem("qualifier_multiple_patterns")

        if len(res["templates"]) and len(res["patterns"]):
            self.flag_problem("qualifier_text_and_template")

        for item in res["templates"]:
            if item.name in ["label", "lb", "lbl"]:
                # TODO: support special separator values "_", "and", "or"
                # probably not needed here, but when q[] is reassembled into text
                q += [ str(x) for x in item.params if x.name not in ["1", "sort", "nocat"] ]
            else:
                q += [ str(x) for x in item.params ]

        q += [
            self.stripformat(x)
            for items in res["patterns"]
            for item in items
            for x in self.stripformat(item).split(",")
        ]

        if "|" in "_".join(q):
            self.flag_problem("qualifier_has_bar", text)
            q = []

        return (q, res["text"])

    def extract_gloss(self, text):
        res = self.extract_templates_and_patterns(["gl", "gloss"], [], text)
        gloss = []
        for item in res["templates"]:
            gloss += map(str, item.params)

        return (gloss, res["text"])

    def get_link(self, text):
        link = Link(text, name="1", parent=self)
#        return link
        d = { item: getattr(link, item) for item in ["target", "alt", "tr", "gloss"] if getattr(link,item) }
        return d
