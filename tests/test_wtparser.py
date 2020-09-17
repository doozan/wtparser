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

from ..utils import parse_anything
from .. import parse, parse_page, parse_language
from ..sections import WiktionarySection
from ..sections.page import Page
from ..sections.language import LanguageSection
from ..sections.nym import NymSection
from ..sections.pos import PosSection
from ..wtnodes.wordsense import WordSense
from ..wtnodes.defitem import DefinitionItem
from ..wtnodes.nymline import NymLine
from ..wtnodes.decoratedlink import DecoratedLink
from ..wtnodes.nymsense import NymSense
from ..wtcode import WTcode


orig_text = """==English==

Blah

==Spanish==

===Adjective===
{{es-adj}}

# [[adj1]]
#: {{syn|es|adjsyn1}}
# {{lb|es|Spain}} [[adj2]], [[adj3]]

===Noun===

{{es-noun|m}}

# [[noun1]]

====Synonyms====
* {{sense|noun1}} {{l|es|nounsyn1}}
* [[nounsyn2]] (noun1)
* {{l|es|nounsyn3}} {{gloss|noun1}}

===Verb===
{{es-verb|verb|er}}

# {{lb|es|Mexico}} to [[verb1]] {{gloss|when doing a thing}}
#: {{syn|es|verbsyn1|verbsyn2|q2=blah}}

==FakeLang==
{{sillytemplate}}

===Boop===
# [[blah]]
"""


def print_children(node, contexts=False, restrict=None, parent=None, depth=0):
        """Iterate over all child :class:`.Node`\\ s of a given *node*."""
        print("*    "*depth, node.__class__, node[:8])
        if restrict and isinstance(node, restrict):
            return
        for code in node.__children__():
            print("====="*depth, code.__class__)
            for child in code.nodes:
#                print("+    "*depth, child.__class__)
                print_children(child, contexts, restrict, parent, depth=depth+1)


def test_filter():
    wikt = parse_anything(orig_text)
    assert str(wikt) == orig_text

    page = Page(wikt, "myword")
    assert str(page) == orig_text

    page = parse_page(orig_text, "myword")
    assert str(page) == orig_text

    wikt = parse(page)
    assert str(wikt) == orig_text

    # Make sure we can find everything from the top node
    assert len(wikt.filter(forcetype=WiktionarySection)) == 9
    assert len(wikt.filter_sections()) == 9

    assert len(wikt.filter(forcetype=LanguageSection)) == 3
    assert len(wikt.filter_languages()) == 3

    assert len(wikt.filter(forcetype=PosSection)) == 3
    assert len(wikt.filter_pos()) == 3

    assert len(wikt.filter(forcetype=WordSense)) == 4
    assert len(wikt.filter_wordsenses()) == 4

    assert len(wikt.filter(forcetype=DefinitionItem)) == 6
    assert len(wikt.filter_defitems()) == 6

    assert len(wikt.filter(forcetype=NymLine)) == 2
    assert len(wikt.filter_nymlines()) == 2

    assert len(wikt.filter(forcetype=DecoratedLink)) == 3
    assert len(wikt.filter_decoratedlinks()) == 3

    assert len(wikt.filter(forcetype=NymSection)) == 1
    assert len(wikt.filter_nyms()) == 1

    assert len(wikt.filter(forcetype=NymSense)) == 3
    assert len(wikt.filter_nymsenses()) == 3


def test_ifilter():

    page = parse_page(orig_text, "test")
    assert len(list(page.ifilter(recursive=False, forcetype=LanguageSection, matches=lambda x: hasattr(x, 'name') and x.name=="Spanish"))) == 1

    assert len(list(page.ifilter(forcetype=WiktionarySection, matches=lambda x: hasattr(x, 'name') and x.name=="Adjective"))) == 1
    assert len(list(page.ifilter(forcetype=WiktionarySection, matches=lambda x: hasattr(x, 'name') and x.name=="Synonyms"))) == 1
    assert len(list(page.ifilter(forcetype=PosSection))) == 3
    assert len(list(page.ifilter(recursive=False, forcetype=WiktionarySection, matches=lambda x: hasattr(x, 'name') and x.name=="Adjective"))) == 0
    assert len(list(page.ifilter(recursive=False, forcetype=WiktionarySection, matches=lambda x: hasattr(x, 'name') and x.name=="Synonyms"))) == 0


def test_parse():

    page = parse_page(orig_text, "test")

    def attr_is(obj, attr, value):
        return hasattr(obj, attr) and getattr(obj ,attr) == value

    def name_is(obj, value):
        return attr_is(obj, "name", value)

    spanish = next(page.ifilter_languages(matches=lambda x: name_is(x,"Spanish")))
    assert spanish.name == "Spanish"
    assert spanish._level == 2

#    for i,child in enumerate(spanish._children):
#        for node in child.nodes:
#            print(i, child.__class__, node.__class__, node.name)
    assert len(spanish._children) == 4

    adj_text = str(next(spanish.ifilter_pos(recursive=False, matches=lambda x: name_is(x, "Adjective"))))
    noun_text = str(next(spanish.ifilter_pos(recursive=False, matches=lambda x: name_is(x, "Noun"))))
    verb_text = str(next(spanish.ifilter_pos(recursive=False, matches=lambda x: name_is(x, "Verb"))))

    noun = next(spanish.ifilter_pos(recursive=False, matches=lambda x: name_is(x, "Noun")))
    assert str(noun) == "===Noun===\n\n{{es-noun|m}}\n\n# [[noun1]]\n\n====Synonyms====\n* {{sense|noun1}} {{l|es|nounsyn1}}\n* [[nounsyn2]] (noun1)\n* {{l|es|nounsyn3}} {{gloss|noun1}}\n\n"
    assert noun == noun_text

    nymsection = next(noun.ifilter_nyms(matches=lambda x: name_is(x, "Synonyms")))
    nym_text = "====Synonyms====\n* {{sense|noun1}} {{l|es|nounsyn1}}\n* [[nounsyn2]] (noun1)\n* {{l|es|nounsyn3}} {{gloss|noun1}}\n\n"
    assert nymsection == nym_text

    adj = next(spanish.ifilter_pos(recursive=False, matches=lambda x: name_is(x, "Adjective")))
    assert adj.name == "Adjective"
    assert adj._level == 3
    adj_word = adj.filter_words(recursive=False)[0]
    assert len(adj_word.filter_wordsenses(recursive=False)) == 2

    noun = next(spanish.ifilter_pos(recursive=False, matches="Noun"))
    assert len(noun.filter_wordsenses()) == 1
    noundef = next(noun.ifilter_wordsenses())

    assert str(noundef).strip() == "# [[noun1]]"

    assert len(noun.filter_nyms(recursive=False)) == 1
    synonyms = next(noun.ifilter_nyms(recursive=False, matches="Synonyms"))
    assert len(synonyms.filter_nymsenses(recursive=False)) == 3

    nymsenses = synonyms.filter_nymsenses(recursive=False)
    assert len(nymsenses) == 3

    nymsense = nymsenses[1]
    assert nymsense.strip() == "* [[nounsyn2]] (noun1)"

    all_decoratedlinks = synonyms.filter_decoratedlinks(recursive=True)
    assert len(all_decoratedlinks) == 3

    decoratedlinks = nymsense.filter_decoratedlinks(recursive=False)
    assert len(decoratedlinks) == 1
    decoratedlink = decoratedlinks[0]
    assert decoratedlink.strip() == "[[nounsyn2]] (noun1)"
    decoratedlink.link = "newsyn"
    assert decoratedlink.strip() == "{{l|es|newsyn}} {{q|noun1}}"

    #assert nymsense.make_tag() == "{{syn|es|newsyn|q1=blah1|nounsyn2|q2=blah2}}"
    assert nymsense.strip() == "* {{l|es|newsyn}} {{q|noun1}}"

    adj = next(spanish.ifilter_pos(recursive=False, matches="Verb"))
    assert adj.name == "Verb"
    assert adj._level == 3
    assert len(adj.filter_wordsenses()) == 1


def test_grey():
    orig_text="""==Spanish==
{{wikipedia|lang=es}}

===Etymology===
From {{der|es|la|grege}}, singular ablative of {{m|la|grex}}.

===Pronunciation===
* {{IPA|es|[ˈɡre̞j]}}

===Noun===
{{es-noun|f|greyes}}

# {{lb|es|obsolete|poetic}} [[flock]], [[herd]]
# {{lb|es|religion}} [[flock]] (people served by a pastor, priest, etc., also all believers in a church or religion)

====Synonyms====
* {{sense|animals}} {{l|es|rebaño}}, {{l|es|rehala}}
* {{sense|religion}} {{l|es|rebaño}}, {{l|es|feligresía}}, {{l|es|congregación}}, {{l|es|iglesia}}

====Derived terms====
* {{l|es|gregario}}
* {{l|es|agregar}}

====Related terms====
* {{l|es|oveja}}
* {{l|es|cabra}}

====See also====
* {{sense|animals}} {{l|es|ganado}}, {{l|es|hato}}, {{l|es|parvada}}, {{l|es|manada}}, {{l|es|jauría}}, {{l|es|cardumen}}, {{l|es|enjambre}}
"""

    entry = parse_language(orig_text, skip_style_tags=True)

#    print_children(entry)
#    for word in entry.ifilter_pos():
#        print("def")

#    raise ValueError()
#


def test_modify_section_during_iteration():
    orig_text="""==Spanish==

===Noun===
{{es-noun}}

# [[word1]]

====Synonyms====
* {{sense|sense1}} {{l|es|syn1}}
* {{sense|sense2}} {{l|es|syn2}}
"""

    entry = parse_language(orig_text, skip_style_tags=True)

    for word in entry.ifilter_pos():
        all_defs = word.filter_wordsenses(recursive=False)
        all_nyms = word.filter_nyms(matches="Synonyms")
        for nym in all_nyms:
            senses = nym.filter_nymsenses()
            for nymsense in senses:
                defs = word.get_defs_matching_sense(nymsense.sense)
                if not len(defs):
                    if nymsense.sense == "":
                        defs = all_defs
                    else:
                        defs = [ all_defs[0] ]

                d = defs[0]
                d.add_nymsense(nymsense)
            word.remove_child(nym)

    new_text="===Noun===\n{{es-noun}}\n\n# [[word1]]\n#: {{syn|es|syn1|syn2}}\n\n"
    assert str(word) == new_text


def test_modify_section_during_iteration():

    orig_text="""
==Spanish==

===Etymology===
From an earlier {{m|es||*ruino}}, from {{m|es|ruina}}, or from a {{inh|es|VL.|-}} root {{m|la||*ruīnus}}, ultimately from {{inh|es|la|ruīna}}. Compare {{cog|pt|ruim}}, {{cog|ca|roí}}.

===Pronunciation===
* {{es-IPA|ruín}}

====Adjective====
{{es-adj|pl=ruines}}

# [[contemptible]], [[mean]], [[heartless]]
# [[mean]], [[stingy]]
# [[wild]]; [[unruly]]
# [[rachitic]]

====Synonyms====
* {{sense|contemptible}} {{l|es|vil}}, {{l|es|despreciable}}
* {{sense|stingy}} {{l|es|avaro}}, {{l|es|mezquino}}, {{l|es|tacaño}}

---
"""


    entry = parse_language(orig_text, skip_style_tags=True)

    for pos in entry.ifilter_pos():
        word = pos.filter_words(recursive=False)[0]
        all_defs = word.filter_wordsenses(recursive=False)
        print(word.name)
        assert len(all_defs) > 0
        all_nyms = word.filter_nyms(matches="Synonyms")
        for nym in all_nyms:
            senses = nym.filter_nymsenses()
            for nymsense in senses:
                defs = word.get_defs_matching_sense(nymsense.sense)
                if not len(defs):
                    if nymsense.sense == "":
                        defs = all_defs
                    else:
                        print("all defs: ", len(all_defs))
                        defs = [ all_defs[0] ]

                d = defs[0]
                d.add_nymsense(nymsense)
            word.remove_child(nym)

    new_text="x"
   # assert str(word) == new_text


def test_deep_subsections():

    orig_text="""
==Spanish==

===Adjective===
{{es-adj}}

# [[word1]]

=====Synonyms=====
* {{l|es|syn1}}

====Subsection====
* blah

=====Sub-Subsection=====
* blah

===Noun===
{{es-noun}}

# [[word2]]

"""

    entry = parse_language(orig_text, skip_style_tags=True)
    word = entry.filter_pos()[0]
    assert "Synonyms" in word._sections
