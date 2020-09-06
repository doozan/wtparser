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
This handles links to wiktionary words including the link, qualifier, and gloss
"""

import re
import json

from . import WiktionaryNode
from ..utils import parse_anything

# from ..parse import parse as wtparse
# from wiktionaryparser import parse as wtparse

# Consider the presence of any non-whitespace or separator to be text
def has_text(text):
    return re.search(r"[^\s,;]", text)


class WordLink(WiktionaryNode):
    def __init__(self, text, name, parent):
        super().__init__(text, name, parent)
        self._has_changed = False

        self._children = []

        self._text = text

        # Link is a dict containing, at mininum, "target" and, optionally, "tr" and "alt" values
        self._link = {}
        self.qualifiers = []
        self.gloss = []
        self.trailing = None

        self._parse_data(text)

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
        res = re.match(r"See \[\[(Thesaurus:[^\]]+)\]\]\.?\s*$", text)
        if res:
            self._link = {"target": res.group(1)}
            return

        gloss, text = self.extract_gloss(text)
        qualifiers, text = self.extract_qualifiers(text)
        link = self.get_link(text)

        if not link or link == {}:
            self.flag_problem("missing_link", text)
        else:
            if "[" in link["target"]:
                self.flag_problem("link_has_bracket", link["target"])
            if "{" in link["target"]:
                self.flag_problem("link_has_brace", link["target"])

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
        res = self.extract_templates_and_patterns(
            ["i", "q", "qual", "qualifier"], [r"\(([^)]*)\)"], text
        )
        q = []

        if len(res["templates"]) > 1:
            self.flag_problem("qualifier_multiple_templates")

        if len(res["patterns"]) > 1:
            self.flag_problem("qualifier_multiple_patterns")

        if len(res["templates"]) and len(res["patterns"]):
            self.flag_problem("qualifier_text_and_template")

        for item in res["templates"]:
            for x in item.params:
                q.append(str(x))

        q += [
            self.stripformat(x)
            for items in res["patterns"]
            for item in items
            for x in item.split(",")
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

        links = []
        wikt = parse_anything(text, skip_style_tags=True)

        templates = wikt.filter_templates(recursive=False)
        for template in templates:
            if template.name in ["l", "link"]:
                if template.get("1") != self.lang_id:
                    self.flag_problem("link_wrong_lang")
                links.append(template)

            # Tags that can be ignored
            elif template.name in [ "g", "rfgender", "sense" ]:
                pass

            else:
                self.flag_problem("link_unexpected_template", text)

            wikt.remove(template)

        text_outside_templates = str(wikt)
        has_text_outside_templates = has_text(text_outside_templates)

        if len(links) == 1 and not has_text_outside_templates:
            _convert = {
                "2": "target",
                "3": "alt",
                "4": "gloss",
                "t": "gloss",
                "tr": "tr",
            }
            return {
                new: str(links[0].get(old))
                for old, new in _convert.items()
                if links[0].has(old) and str(links[0].get(old)).strip() != ""
            }

        if len(links) > 2:
            self.flag_problem("link_multiple_templates")

        # If there's anything except a solitary template, strip all templates to text and process
        # the line as a text link. Flag if any information is lost in the process
        wikt = parse_anything(text, skip_style_tags=True)
        for template in wikt.filter_templates(recursive=False):
            if template.name in ["l", "link"]:
                for p in ["3", "4", "t", "tr"]:
                    if template.has(p) and template.get(p).strip() != "":
                        self.flag_problem(f"link_has_param_{p}", str(template))
                name = template.get("2")
                wikt.replace(template, name)
            else:
                wikt.remove(template)

        text = re.sub(r"\s+", " ", str(wikt)).strip()

        # Replace "[[word|fancy word]]" with "word"
        orig_text = text
        remaining_text = text_outside_templates
        for match in re.findall(r"\[\[[^[\]]+\]\]", text):
            target = re.escape(match)
            replacement, junk, extra = match[2:].strip("]]").partition("|")
            if extra:
                self.flag_problem(f"bracket_has_alt", match)
            text = re.sub(target, replacement, text)
            remaining_text = re.sub(target, "", remaining_text)

        has_bracketed_text = text != orig_text
        has_text_links = has_text(remaining_text)

        sources = []
        if len(links):
            sources.append("template")
        if has_bracketed_text:
            sources.append("brackets")
        if has_text_links:
            sources.append("text")
        if len(sources) > 1:
            self.flag_problem("link_has_" + "_and_".join(sources))

        text = " ".join([self.stripformat(x) for x in text.split(" ")])
        if "|" in text:
            self.flag_problem("link_has_pipe", text)
            text = text.split("|", 1)[0]

        if text == "":
            return None

        return {"target": text}
