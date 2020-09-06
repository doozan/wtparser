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
This handles nym lines in definitions
Expects line like:
#: {{nymtemplate}}
"""

from .defitem import DefinitionItem
from .nymsense import NymSense
from ..constants import NYM_TO_TAG
from ..utils import parse_anything
from ..sections.nymsection import NymSection


class NymLine(DefinitionItem):
    """
    Handles "nym" lines in definitions:
    #: {{syn|es|word|word2}}
    """
    @classmethod
    def from_items(cls, tmpl_name, lang_id, items, name, parent):
        self = cls(None, name, parent)
        text = "#: " + self.items_to_nymtemplate(tmpl_name, lang_id, items) + "\n"
        self._parse_data(text)
        return self

    @classmethod
    def from_nymsense(cls, nymsense, name, parent):
        tmpl_name = NYM_TO_TAG[nymsense.get_ancestor(NymSection).name]
        lang_id = nymsense.lang_id
        items = [
            wordlink.item
            for wordlink in nymsense.filter_wordlinks()
            if "target" in wordlink.item
        ]

        if not len(items):
            parent.flag_problem("nymsense_is_empty", nymsense)

        return cls.from_items(tmpl_name, lang_id, items, name, parent)

    def _parse_data(self, text):
        self._children = [ parse_anything(text) ]

        if not text.startswith("#:"):
            self.flag_problem("unexpected_line_start", text)

        # Verify there's only one template
        templates = self.filter_templates(recursive=False)
        if not len(templates):
            self.flag_problem("no_template")
            return
        elif len(templates) > 2:
            self.flag_problem("too_many_templates")

        self.type = templates[0].name

        # TODO: ensure there's no other text on the line

    def add_nymsense(self, nymsense):
        items = [wordlink.item for wordlink in nymsense.filter_wordlinks()]
        if not len(items):
            self.flag_problem("no_items_in_nymsense", nymsense)
            return
        self.add(items)

    def add_nymline(self, nymline):
        # TODO: check that lang_id and template type match
        self.add(nymline.items)

    def add(self, newitems):
        if not isinstance(newitems, list):
            newitems = [newitems]

        template = next(self.ifilter_templates(recursive=False))
        tmpl_name = str(template.name)
        lang_id = str(template.get("1"))
        items = self.nymtemplate_to_items(template)

        for newitem in newitems:
            if not newitem:
                continue
            if any([x for x in items if x["target"] == newitem["target"]]):
                self.flag_problem("autofix_skip_duplicate_values", {"ignored": newitem, "existing": items, "newitems": newitems, "tmpl": template})
            else:
                items.append(newitem)

        # The nym template requires any Thesaurus: entries to be the last paramater
        # and to have no alt/tr/etc modifiers
        thesaurus = []
        for idx, item in enumerate(items):
            if item["target"].startswith("Thesaurus:"):
                thesaurus.append(items.pop(idx))

        if len(thesaurus) > 1:
            raise ValueError(
                "Nym template only supports one Thesaurus: entry", thesaurus
            )

        items += thesaurus

        wikt = parse_anything(self.items_to_nymtemplate(tmpl_name, lang_id, items))
        new_template = wikt.filter_templates(recursive=False)[0]

        self.replace_child(template, new_template)

    @property
    def items(self):
        template = next(self.ifilter_templates(recursive=False))
        # TODO: Verify template is a nym template
        return self.nymtemplate_to_items(template)

    def nymtemplate_to_items(self, template):
        """
        Parses a Wikicode *nym template into targets with any available properties
        {{syn|es|word|q1=qual|word2|tr2=tr}}
        [ { "target": "word", "q": "qual" }, { "target": "word2", "tr": "tr" } ]
        """
        res = []
        params = template.params
        for param in params:
            if not str(param.name).isdigit():
                continue
            i = int(str(param.name))
            if i == 1:
                continue

            item = {
                k: str(template.get(p).value)
                for k, p in {
                    "target": str(i),
                    "alt": f"alt{i-1}",
                    "tr": f"tr{i-1}",
                    "q": f"q{i-1}",
                }.items()
                if template.has(p)
            }

            res.append(item)

        return res

    def items_to_nymtemplate(self, tmpl_name, lang_id, items):
        """
        Combines a list of items into a nym template
        item is a list of items, where each item is a dict with at least "target"
        and, optionally, "alt", "tr", and "q" params
        """
        params = [tmpl_name, lang_id]
        for idx, item in enumerate(items, 2):
            params.append(item["target"])

            for k,v in item.items():
                if k in ["target"]:
                    continue
                if k in ["alt", "tr", "q"] and v:
                    params.append(f"{k}{idx-1}={item[k]}")
                elif k == "gloss":
                    if "q" not in item or not item["q"]:
                        params.append(f"q{idx-1}={item[k]}")
                        print("ERRR:", self.__class__, "using_gloss_as_qualifier", self._parent._parent._parent.name)
                        self.flag_problem("using_gloss_as_qualifier", item)

                        print("parent probs:", self._parent.problems)
                        for child in self._parent._children:
                            for node in child.nodes:
                                if node is self:
                                    print("me")
                                else:
                                    print(node.__class__)

                    else:
                        self.flag_problem("gloss_and_qualifier", item)
                else:
                    self.flag_problem("discarded_data", k, item)

        string = "{{" + "|".join(map(str, params)) + "}}"
        return string
