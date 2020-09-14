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
A link to exactly one Wiktionary word
"""

import re

from . import WiktionaryNode
from ..utils import parse_anything

class Link(WiktionaryNode):
    LINK_TEMPLATES = ["l", "link"]
    IGNORE_TEMPLATES = ["g", "rfgender"]

    # The presence of any non-filler character is considered "text" that
    # needs to be parsed
    DELIMITER_CHARS = r"\s" + re.escape(".,:;()")
    FILLER = "[" + DELIMITER_CHARS + "]"
    NOT_FILLER = "[^" + DELIMITER_CHARS + "]"

    BRACKET_PATTERN = rf"""(?x)
        (?P<prefill>{FILLER}*)      # Whitespace/separators
        (?P<bracket>
            (?P<prefix>[^\s]*)      # (optional) link prefix
            \[\[                    # Opening [[
            \s*                     # Whitespace
            (?P<contents>[^\]]+?)   # Any character except ]
            \s*                     # Whitespace
            \]\]                    # Closing ]]
            (?P<trail>[^\s]*)       # (optional) link trails
        )
        (?P<postfill>{FILLER}*)     # Whitespace/separators
        """

    def __init__(self, text, name, parent):
        """ A link to exactly one wiktionary word
        Expects {{template}}, [[bracketed]], or bare link
        Returns dict containing "target" and (optionally) "alt", "gloss", and "tr"
        """

        self.target = None
        self.alt = None
        self.gloss = None
        self.tr = None

        self._orig = text
        self._has_changed = False

        super().__init__(text, name, parent)

    def _parse_data(self, text):

        if self.is_single_template(text):
            self.parse_template(text)

        elif self.is_single_bracket(text):
            self.parse_bracket(text)

        elif self.is_only_text(text):
            self.flag_problem("link_is_only_text")
            self.target = text.strip()

        else:
            self.flag_problem("link_is_complicated")
            text = self.templates_to_text(text)
            text = self.brackets_to_text(text)
            self.target = text.strip()

        pattern = "[" + re.escape("[]{}()#$!/_:,;") + "]"
        if re.search(pattern, self.target):
            self.flag_problem("link_has_unexpected_characters", self.target)

    def parse_template(self, text):
        for k,v in self.template_to_dict(text).items():
            setattr(self, k, v)

    def parse_bracket(self, text):
        for k,v in self.bracket_to_dict(text).items():
            setattr(self, k, v)

    def __unicode__(self):
#        if self._has_changed:
#            results = []
#            if self._link:
#                results.append(self.get_formatted_link())
#            if self.qualifiers:
#                results.append(self.get_formatted_qualifiers())
#            return " ".join(results)
#        else:
            return self._text

    @staticmethod
    def is_only_text(text):
        """ Returns True if text contains no brace pairs {{ }} and no bracket pairs [[ ]] """
        return not re.search(r"(\[\[[^]]+\]\]|\{\{[^}]+\}\})", text)

    @staticmethod
    def is_single_template(text):
        """Text is considered to be a single template if:
        1) it has exactly one link template
        2) it has no other, non-ignorable templates
        3) there is no text outside the link template, except for (optional) prefix and suffix text
        """

        wikt = parse_anything(text)

        # Exactly one link template
        links = wikt.filter_templates(recursive=False, matches=lambda x: x.name in Link.LINK_TEMPLATES)
        if len(links) != 1:
            return False

        # No non-link, non-ignorable templates
        expected_templates = Link.LINK_TEMPLATES + Link.IGNORE_TEMPLATES
        if any(wikt.ifilter_templates(recursive=False, matches=lambda x: x.name not in expected_templates)):
            return False

        # No text outside template except prefix and suffix text
        # remove ignorable templates
        for template in wikt.ifilter_templates(recursive=False, matches=lambda x: x.name in Link.IGNORE_TEMPLATES):
            wikt.remove(template)

        d = Link.template_to_dict(wikt)
        wikt.remove(d["raw"])

        return not re.search(Link.NOT_FILLER, str(wikt))

    @staticmethod
    def get_valid_template_prefix(text):
        return text

    @staticmethod
    def get_valid_template_trail(text):
        return text

    @staticmethod
    def get_valid_bracket_prefix(text):
        return text

    @staticmethod
    def get_valid_bracket_trail(text):
        return text

    @staticmethod
    def template_to_dict(template):
        """ Returns link dict from the first link template encountered in text """
        wikt = parse_anything(template, skip_style_tags=True)
        link = next(wikt.ifilter_templates(recursive=False, matches=lambda x: x.name in Link.LINK_TEMPLATES))
        _convert = {
            "2": "target",
            "3": "alt",
            "4": "gloss",
            "t": "gloss",
            "tr": "tr",
        }

        d = { new: str(link.get(old)) for old, new in _convert.items() if link.has(old) and str(link.get(old)).strip() }

        # Check for prefix/trail text attached to the link
        # prefix{{template|stuff}}trail
        # If any exists, use it to build alt-text with the contents of the template
        pattern = r"(?P<prefix>[^\s]*)(?P<link>" + re.escape(str(link)) + r")(?P<trail>[^\s]*)"
        res = re.search(pattern, str(template))
        prefix = Link.get_valid_template_prefix(res.group('prefix')) if res.group('prefix') else ""
        trail = Link.get_valid_template_trail(res.group('trail')) if res.group('trail') else ""

        if "alt" not in d and (prefix or trail):
            d["alt"] = prefix + d["target"] + trail
            d["raw"] = prefix + str(link) + trail
        else:
            d["raw"] = str(link)

        return d

    @staticmethod
    def is_single_bracket(text):
        return re.match(f"{Link.BRACKET_PATTERN}$", text, re.DOTALL)

    @staticmethod
    def template_to_text(template):
        link = Link.template_to_dict(template)
        if "alt" in link:
            return link["alt"]
        if "tr" in link:
            return link["tr"]
        return link["target"]

    @staticmethod
    def templates_to_text(text):
        wikt = parse_anything(text, skip_style_tags=True)
        for template in wikt.ifilter_templates(recursive=False):
            if template.name in Link.LINK_TEMPLATES:
                wikt.replace(template, Link.template_to_text(template))
            else:
                wikt.remove(template)
        return str(wikt)

    @staticmethod
    def bracket_to_dict(text):
        """ Returns a link item from the first bracketed word found in text """
        res = re.search(Link.BRACKET_PATTERN, text)
        if not res:
            raise ValueError("brackets not found in", text)
        link, junk, alt = res.group('contents').partition("|")
        prefix = Link.get_valid_bracket_prefix(res.group('prefix')) if res.group('prefix') else ""
        trail = Link.get_valid_bracket_trail(res.group('trail')) if res.group('trail') else ""

        if not prefix and not trail and not alt:
            return { "target": link }

        if not prefix and not trail:
            return { "target": link, "alt": alt }

        if not alt:
            return { "target": link, "alt": prefix+link+trail }

        return { "target": link, "alt": alt }

    @staticmethod
    def bracket_to_text(text):
        link = Link.bracket_to_dict(text)
        return link["alt"] if "alt" in link else link["target"]

    @staticmethod
    def brackets_to_text(text):
        replacements = []
        for match in re.finditer(Link.BRACKET_PATTERN, text):
            bracket = match.group("bracket")
            replacements.append( [bracket, Link.bracket_to_text(bracket)] )

        for old,new in replacements:
            text = text.replace(old, new)

        return text

