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
import re
from itertools import chain

import mwparserfromhell
from mwparserfromhell.nodes import Node
from ..utils import parse_anything, template_aware_splitlines

from mwparserfromhell.nodes import Template

class WiktionaryNode(Node):
    def __init__(self, text, name, parent):
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

    def __children__(self):
        return self._children

    def __unicode__(self):
        return "".join(map(str, self._children))

    @property
    def name(self):
        return self._name

    @property
    def lang_id(self):
        if hasattr(self, "_lang_id"):
            return self._lang_id

        return self.get_ancestor_attr("_lang_id", "ERROR")


    def flag_problem(self, problem, *data):
        flag_problem = self.get_ancestor_attr("flag_problem")
        if flag_problem:
            print("ERROR:", problem, data, self.__class__)
            return flag_problem(problem, *data)
        else:
            #raise ValueError(problem, data)
            print("UNHANDLED ERROR:", problem, data, self.__class__)

#        self.problems[problem] = self.problems.get(problem, []) + [data]

    @property
    def problems(self):
        problems = self.get_ancestor_attr("problems")
        if problems is not None:
            return problems
        else:
            raise ValueError("No ancestor found to provide 'problems'", self.__class__)

    def is_good(self):
        return True
        return self._err.is_good()

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
from ..sections.word import WordSection
from ..sections.nymsection import NymSection
from .definition import Definition
from .defitem import DefinitionItem
from .nymline import NymLine
from .nymsense import NymSense
from .wordlink import WordLink

WiktionaryNode._build_filter_methods(
    sections=WiktionarySection,
    languages=LanguageSection,
    words=WordSection,
    defs=Definition,
    defitems=DefinitionItem,
    nymlines=NymLine,
    nyms=NymSection,
    senses=NymSense,
    wordlinks=WordLink,
    templates=Template,
    #    arguments=Argument, comments=Comment, external_links=ExternalLink,
    #    headings=Heading, html_entities=HTMLEntity, tags=Tag, templates=Template,
    #    text=Text, wikilinks=Wikilink)
)
