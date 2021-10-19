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

# import logging
import copy
import re
from itertools import chain

import mwparserfromhell
from mwparserfromhell.nodes import Node
#from ..wtcode import WTcode
from ..utils import parse_anything, template_aware_splitlines

from mwparserfromhell.nodes import Template

class WiktionaryNode(Node):

    # List of "standalone" templates that may appear between a section heading
    # the actual content of that section
    ignore_templates = [
        "attention",
        "c",
        "C",
        "categorize",
        "catlangname",
        "catlangcode",
        "checksense",
        "cln",
        "DEFAULTSORT",
        "element",
        "enum",
        "hot word",
        "IPA",
        "multiple images",
        "no entry",
        "number box",
        "phrasebook",
        "picdic",
        "picdiclabel",
        "picdiclabel/new",
        "rfd",
        "rfe",
        "rfi",
        "rfinfl",
        "rfp",
        "rfquote",
        "rfv",
        "root",
        "slim-wikipedia",
        "top",
        "topic",
        "topics",
        "was fwotd",
        "wikidata",
        "wikipedia",
        "Wikipedia",
        "wikiversity",
        "wp",
        ]
    re_items = [ r"\{\{\s*"+item+r"\s*\|" for item in ignore_templates ] #}}
    ignore_template_pattern = re.compile("(" + "|".join(re_items) + ")")

    ignore_links = [ "Category:", "File:", "Image:" ]
    re_items = [ r"\[\[\s*"+item+r"" for item in ignore_links ]
    ignore_link_pattern = re.compile("(" + "|".join(re_items) + ")")


    def __init__(self, text, name, parent, parse_data=True):

        self._text = text
        self._name = name
        self._parent = parent
        self._children = []


    #        self._logname = parent._logname+"."+str(name) if parent else str(name)
    #        self.log = logging.getLogger(self._logname)

    #        ancestor = self
    #        tree = []
    #        while ancestor:
    #            tree.insert(0, ancestor.name)
    #            ancestor = ancestor.parent
    #        logname = ".".join(tree)

    #        self._err = ErrorHandler()


        if text is not None and parse_data:
            self._parse_data(text)

    def _parse_data(self, text):
        self.add_text(text)

    def __children__(self):
        return self._children

    def __unicode__(self):
        return "".join(map(str, self._children))

    @property
    def name(self):
        return self._name

    @property
    def lang_id(self):
        if not hasattr(self, "_lang_id"):
            self._lang_id = self.get_ancestor_attr("_lang_id", "ERROR")
        return self._lang_id

    @property
    def lang(self):
        if not hasattr(self, "_lang"):
            self._lang = self.get_ancestor_attr("_lang", None)
        return self._lang

    @property
    def page_title(self):
        from ..sections.page import Page
        if not hasattr(self, "_page_title"):
            self._page_title = self.get_ancestor(Page)._name
        return self._page_title

    def flag_problem(self, problem, *data, from_child=False):
        flag_problem = self.get_ancestor_attr("flag_problem")
        if flag_problem:
            flag_problem(problem, *data, from_child=True)

        if not from_child:
            if not hasattr(self, "_local_problems"):
                self._local_problems = {}
            self._local_problems[problem] = self._local_problems.get(problem, []) + [data]

        if not hasattr(self, "_problems"):
            self._problems = {}
        self._problems[problem] = self._problems.get(problem, []) + [data]


    @property
    def problems(self):
        if not hasattr(self, "_problems"):
            self._problems = {}
        return self._problems

    @property
    def local_problems(self):
        if not hasattr(self, "_local_problems"):
            self._local_problems = {}
        return self._local_problems

    def get_ancestor(self, target):
        """Returns the nearest ancestor of class ``target``"""

        ancestor = self._parent
        while ancestor is not None:
            if isinstance(ancestor, target):
                return ancestor
            ancestor = ancestor._parent if hasattr(ancestor, "_parent") else None

    def get_ancestor_attr(self, target, default=None):
        """
        Returns the ``target`` attr of nearest ancestor able to provide it
        Returns ``default`` if not found
        """
        ancestor = self._parent
        while ancestor is not None:
            if hasattr(ancestor, target):
                return getattr(ancestor, target)
            ancestor = ancestor._parent if hasattr(ancestor, "_parent") else None

        return default

    def get_matching_ancestor(self, matches):
        """
        Returns nearest ancestor satisfying the matches function
        """
        ancestor = self._parent
        while ancestor is not None:
            if matches(ancestor):
                return ancestor
            ancestor = ancestor._parent if hasattr(ancestor, "_parent") else None
        return None

    def add_text(self, lines):
        if not lines:
            return

        item = "".join(lines)
        self._children.append(parse_anything(item))

    def remove_child(self, obj, recursive=True, warn=True):
        """Remove *obj* from the list of nodes.
        """
        for child in self._children:
            for i, node in enumerate(child.nodes):
                if node is obj:
                    child.nodes.pop(i)
                    return True
                elif recursive:
                    if hasattr(node, "remove_child") and node.remove_child(
                        obj, recursive, warn=False
                    ):
                        return True
        if warn:
            raise ValueError("item not found")

    def replace_child(self, target, new):
        for child in self._children:
            for i, node in enumerate(child.nodes):
                if node is target:
                    child.nodes[i] = new
                    return
        raise ValueError("item not found")

    def replace_child_with_list(self, target, new):
        """ Replace child object with multiple objects """
        for child in self._children:
            for i, node in enumerate(child.nodes):
                if node is target:
                    child.nodes[i] = new[0]
                    for item in reversed(new[1:]):
                        child.nodes.insert(i+1, item)
                    return
        raise ValueError("item not found")

    def insert_after(self, target, new):
        for child in self._children:
            for i, node in enumerate(child.nodes):
                if node is target:
                    child.nodes.insert(i+1, new)
                    return
        raise ValueError("item not found", self._name)

    def insert_before(self, target, new):
        for child in self._children:
            for i, node in enumerate(child.nodes):
                if node is target:
                    child.nodes.insert(i, new)
                    return
        raise ValueError("item not found", self._name)

    @staticmethod
    def pop_leading_newlines(items):
        """ Pop leading whitespace-only items from list of strings """
        res = []
        while re.match(r"^\s*$", items[0]):
            res.append(items.pop(0))
        return res

    @staticmethod
    def pop_trailing_newlines(items):
        """ Pop trailing whitespace-only items from list of strings """
        res = []
        idx = len(items) - 1
        while idx >= 0 and re.match(r"^\s*$", items[idx]):
            res.insert(0, items.pop(idx))
            idx -= 1
        return res

    @staticmethod
    def _get_children(node, contexts=False, restrict=None, parent=None):
        """Iterate over all child :class:`.Node`\\ s of a given *node*."""
        yield (parent, node) if contexts else node
        if restrict and isinstance(node, restrict):
            return
        for code in node.__children__():
            for child in code.nodes:
                sub = WiktionaryNode._get_children(child, contexts, restrict, code)
                yield from sub

    def _prepare_line(self, line):
        """Hook to modify line before it's passed to the parser"""
        return line

    def _parse_list(self, text):
        """
        Generic line-by-line parser
        """

        current_item = []
        unhandled = []

        in_header = True
        in_footer = False
        self._heading_found = False

        for line in template_aware_splitlines(text, True):
            line = self._prepare_line(line)

            if in_header:
                in_header = self._is_header(line)
                if not in_header and unhandled:
                    self._parse_header(unhandled)
                    unhandled = []

            if in_header or in_footer:
                unhandled.append(line)
                continue

            if re.match(r"\s+$", line):
                if current_item:
                    current_item.append(line)
                else:
                    unhandled.append(line)
                continue

            if current_item:
                if self._is_still_item(line):
                    current_item.append(line)
                    continue
                else:
                    self.add_item(current_item)
                    current_item = []

            if self._is_new_item(line):
                if len(unhandled):
                    self.add_text(unhandled)
                    unhandled = []

                current_item = [line]

            elif self._is_footer(line):
                in_footer=True
                unhandled.append(line)

            # Unexpected text
            else:
                if current_item:
                    self.add_item(current_item)
                    current_item = []

                if not self._handle_other(line):
                    unhandled.append(line)

        if in_header and unhandled:
            self._parse_header(unhandled)
            unhandled = []
        elif current_item:
            self.add_item(current_item)
            current_item = []
        elif len(unhandled):
            self.add_text(unhandled)
            unparsed = []


    def _is_filler_line(self, line):
        if self.ignore_template_pattern and re.match(self.ignore_template_pattern, line):
            return True

        if self.ignore_link_pattern and re.match(self.ignore_link_pattern, line):
            return True

        return False

    def _is_header(self, line):

        if re.match(r"\s+$", line):
            return True

        if not self._heading_found and re.match(r"\s*==*[^=]+==*", line):
            self._heading_found=True
            return True

        if self._is_filler_line(line):
            return True

        return self._is_header_extra(line)

    def _is_header_extra(self, line):
        """Override this to catch additional header items"""
        return False

    def _parse_header(self, lines):
        self.add_text(lines)

    def _is_footer(self, line):

        if self._is_filler_line(line):
            return True

        re_endings = [ r"==[^=]+==", r"----" ]
        endings = "|".join(re_endings)

        if re.match(fr"\s*({endings})", line):
            return True
        return False

    def _is_new_item(self, line):
        return False

    def _is_still_item(self, line):
        return False

    def _handle_other(self, line):
        if self._is_filler_line(line):
            self.add_text(unhandled)
            return True

        self.flag_problem("unhandled_line", line)
        return False

    @staticmethod
    def _build_matcher(matches, flags):
        """Helper for :meth:`_indexed_ifilter` and others.
        If *matches* is a function, return it. If it's a regex, return a
        wrapper around it that can be called with a node to do a search. If
        it's ``None``, return a function that always returns ``True``.
        """
        if matches:
            if callable(matches):
                return matches
            return lambda obj: re.search(matches, str(obj), flags)
        return lambda obj: True

    FLAGS = re.IGNORECASE | re.DOTALL | re.UNICODE
    RECURSE_OTHERS = 2

    def ifilter(self, recursive=True, matches=None, flags=FLAGS, forcetype=None):
        """
        Works like Wikicode ifilter, except:
        searches _children[].nodes instead of .nodes when recursive=False
        """
        match = self._build_matcher(matches, flags)
        if recursive:
            restrict = forcetype if recursive == self.RECURSE_OTHERS else None

            def getter(node):
                for ch in self._get_children(node, restrict=restrict):
                    yield ch

            nodes = chain(*(getter(n) for child in self._children for n in child.nodes))
        else:
            nodes = [n for child in self._children for n in child.nodes]

        for node in nodes:
            if (not forcetype or isinstance(node, forcetype)) and match(node):
                yield node

    def filter(self, *args, **kwargs):
        """Return a list of nodes within our list matching certain conditions.
        This is equivalent to calling :func:`list` on :meth:`ifilter`.
        """
        return list(self.ifilter(*args, **kwargs))

    @classmethod
    def _build_filter_methods(cls, **meths):
        """Given Node types, build the corresponding i?filter shortcuts.
        The should be given as keys storing the method's base name paired with
        values storing the corresponding :class:`.Node` type. For example, the
        dict may contain the pair ``("templates", Template)``, which will
        produce the methods :meth:`ifilter_templates` and
        :meth:`filter_templates`, which are shortcuts for
        :meth:`ifilter(forcetype=Template) <ifilter>` and
        :meth:`filter(forcetype=Template) <filter>`, respectively. These
        shortcuts are added to the class itself, with an appropriate docstring.
        """
        doc = """Iterate over {0}.
        This is equivalent to :meth:`{1}` with *forcetype* set to
        :class:`~{2.__module__}.{2.__name__}`.
        """
        make_ifilter = lambda ftype: (
            lambda self, *a, **kw: self.ifilter(forcetype=ftype, *a, **kw)
        )
        make_filter = lambda ftype: (
            lambda self, *a, **kw: self.filter(forcetype=ftype, *a, **kw)
        )
        for name, ftype in meths.items():
            ifilter = make_ifilter(ftype)
            filter = make_filter(ftype)
            ifilter.__doc__ = doc.format(name, "ifilter", ftype)
            filter.__doc__ = doc.format(name, "filter", ftype)
            setattr(cls, "ifilter_" + name, ifilter)
            setattr(cls, "filter_" + name, filter)


from ..sections import WiktionarySection
from ..sections.language import LanguageSection
from ..sections.pos import PosSection
from ..sections.nym import NymSection
from ..sections.usage import UsageSection
from ..sections.etymology import EtymologySection

from .word import Word
from .wordsense import WordSense
from .gloss import Gloss
from .nymline import NymLine
from .nymsense import NymSense
from .decoratedlink import DecoratedLink
from .link import Link
from .usagenote import UsageNote
from .etymology import Etymology

WiktionaryNode._build_filter_methods(
    sections=WiktionarySection,
    languages=LanguageSection,
    etymology_sections=EtymologySection,
    pos=PosSection,
    words=Word,
    wordsenses=WordSense,
    glosses=Gloss,
    nymlines=NymLine,
    nyms=NymSection,
    nymsenses=NymSense,
    decoratedlinks=DecoratedLink,
    templates=Template,
    links=Link,
    usagenotes=UsageNote,
    etymologies=Etymology,
    #    arguments=Argument, comments=Comment, external_links=ExternalLink,
    #    headings=Heading, html_entities=HTMLEntity, tags=Tag, templates=Template,
    #    text=Text, wikilinks=Wikilink)
)
