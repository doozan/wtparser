#
# Copyright (c) 2022 Jeff Doozan
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

from ... import parse_page
from .. import WiktionarySection

def test_subsections(language):
    orig_text = """==Spanish==

===Noun===
{{es-noun}}

# [[wordA]]

====Synonyms====
* {{l|es|synA}}

=====Subsection=====
* blah1

======Sub-Subsection======
* blah2

{{other stuff}}

=====Subsection2=====
* blah3

=====Subsection3=====
* blah4

"""
    expected_text = """==Spanish==

===Noun===
{{es-noun}}

# [[wordA]]

====Synonyms====
* {{l|es|synA}}

====Subsection====
* blah1

=====Sub-Subsection=====
* blah2

{{other stuff}}

====Subsection2====
* blah3

====Subsection3====
* blah4

"""

    page = parse_page(orig_text, "test", parent=None)
    section = next(page.ifilter_sections(matches=lambda x: hasattr(x, 'name') and x.name=="Synonyms"))
    section.raise_subsections()

    assert section == """\
====Synonyms====
* {{l|es|synA}}

"""

    assert str(page) == expected_text



