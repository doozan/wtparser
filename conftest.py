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

import mwparserfromhell
import pytest

from . import parse_page

sample_page = """==Spanish==

===Adjective===
{{es-adj}}

# [[adj1]]
#: {{syn|es|adjsyn1}}
# {{lb|es|Spain}} [[adj2]], [[adj3]]

===Noun===
{{es-noun}}

# [[noun1]]

====Synonyms====
* [[nounsyn1]] (blah1)
* {{l|es|nounsyn2}} {{q|blah2}}

===Verb===
{{es-verb|verb|er}}

# {{lb|es|Mexico}} to [[verb1]] {{gloss|when doing a thing}}
#: {{syn|es|verbsyn1|verbsyn2|q2=blah}}
"""

@pytest.fixture()
def page():
    return parse_page(sample_page, "myword", parent=None)

@pytest.fixture()
def language(page):
    return next(page.ifilter_languages(recursive=False, matches="Spanish"))

@pytest.fixture()
def word(language):
    return next(language.ifilter_pos(recursive=False, matches="Adjective"))

@pytest.fixture()
def word_with_nymsection(language):
    return next(language.ifilter_pos(recursive=False, matches="Noun"))

@pytest.fixture()
def wordsense(word):
    return next(word.ifilter_wordsenses(recursive=False))

@pytest.fixture()
def nymsection(word_with_nymsection):
    return next(word_with_nymsection.ifilter_nyms(recursive=False))

@pytest.fixture()
def nymsense(nymsection):
    return next(nymsection.ifilter_nymsenses(recursive=False))

@pytest.fixture()
def decoratedlink(nymsense):
    return next(nymsense.ifilter_decoratedlinks(recursive=False))

@pytest.fixture()
def nymline(page):
    return next(page.ifilter_nymlines())
