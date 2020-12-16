from .... import parse_page
from ....utils import parse_anything
from .. import Data

def test_match_headword():
    template = parse_anything("{{es-noun|m}}").filter_templates()[0]
    assert Data.match_headword(template) == True

    template = parse_anything("{{es-adj}}").filter_templates()[0]
    assert Data.match_headword(template) == True

    template = parse_anything("{{es-xxx}}").filter_templates()[0]
    assert Data.match_headword(template) == False

def make_word(word, template):

    data = f"""\
==Spanish==

===Noun===
{template}

# word1\
"""

    wikt = parse_page(data, word, None)
    word = next(wikt.ifilter_words())
    return word

def test_get_gender_and_number():

    word = make_word("test", "{{es-noun|m}}")
    assert Data.get_gender_and_number(word) == ["m"]

    word = make_word("test", "{{es-noun|f}}")
    assert Data.get_gender_and_number(word) == ["f"]

    word = make_word("test", "{{es-noun|g1=m|g2=f}}")
    assert Data.get_gender_and_number(word) == ["m", "f"]

    word = make_word("test", "{{es-noun|m|g1=f}}")
    assert Data.get_gender_and_number(word) == ["m"]

def test_get_form_sources():

    data = """\
==Spanish==

===Verb===
{{es-verb|ten|er|pres=tengo|pret=tuve}}

# {{lb|es|transitive}} to [[have]], [[possess]] {{gloss|literally}}

====Conjugation====
{{es-conj-er||p=tener|combined=1}}
"""

    wikt = parse_page(data, "tener", None)
    word = next(wikt.ifilter_words())
    assert Data.get_form_sources(word) == ["{{es-verb|ten|er|pres=tengo|pret=tuve}}", "{{es-conj-er||p=tener|combined=1}}"]
    word = make_word("testo", "{{es-noun|m|f=testa}}")
    assert Data.get_form_sources(word) == ["{{es-noun|m|f=testa}}"]

