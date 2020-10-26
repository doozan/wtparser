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

def test_get_genders():

    word = make_word("test", "{{es-noun|m}}")
    assert Data.get_genders(word) == ["m"]

    word = make_word("test", "{{es-noun|f}}")
    assert Data.get_genders(word) == ["f"]

    word = make_word("test", "{{es-noun|g1=m|g2=f}}")
    assert Data.get_genders(word) == ["m", "f"]

    word = make_word("test", "{{es-noun|m|g1=f}}")
    assert Data.get_genders(word) == ["m"]


def test_get_adj_forms():
    # Explicit plural
    word = make_word("testo", "{{es-adj|pl=testoz}}")
    assert Data.get_forms(word) == {"pl":["testoz"]}

    # whitespace
    word = make_word("testo", "{{es-adj|pl= testoz }}")
    assert Data.get_forms(word) == {"pl":["testoz"]}
    word = make_word("testo", "{{es-adj| pl=testoz }}")
    assert Data.get_forms(word) == {"pl":["testoz"]}

    # generate plurals
    word = make_word("testo", "{{es-adj|f=testa}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa"], "fpl":["testas"]}

    # use specified feminine plural
    word = make_word("testo", "{{es-adj|f=testa|fpl=testaz}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa"], "fpl":["testaz"]}

    # pl used for pl and fpl
    word = make_word("testo", "{{es-adj|f=testa|pl=testoz}}")
    assert Data.get_forms(word) == {"pl":["testoz"], "f":["testa"], "fpl":["testoz"]}

    # mpl specifies masculine plural
    word = make_word("torpón", "{{es-adj|f=torpona|mpl=torpones}}")
    assert Data.get_forms(word) == {"pl":["torpones"], "f":["torpona"], "fpl":["torponas"]}


def test_get_noun_forms():
    # Explicit plural
    word = make_word("testo", "{{es-noun|m|testoz}}")
    assert Data.get_forms(word) == {"pl":["testoz"]}

    # whitespace
    word = make_word("testo", "{{es-noun|m| testoz }}")
    assert Data.get_forms(word) == {"pl":["testoz"]}

    # Generated plural
    word = make_word("testo", "{{es-noun|m}}")
    assert Data.get_forms(word) == {"pl":["testos"]}

    # Generated plural
    word = make_word("robot", "{{es-noun|m}}")
    assert Data.get_forms(word) == {"pl":["robots"]}

    # No plural
    word = make_word("testo", "{{es-noun|m|-}}")
    assert Data.get_forms(word) == {}

    word = make_word("testa", "{{es-noun|f|testaz}}")
    assert Data.get_forms(word) == {"pl":["testaz"]}

    word = make_word("testa", "{{es-noun|f}}")
    assert Data.get_forms(word) == {"pl":["testas"]}

    word = make_word("testo", "{{es-noun|m|f=testa}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa"], "fpl":["testas"]}

    word = make_word("testo", "{{es-noun|m|f=1}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa"], "fpl":["testas"]}

    word = make_word("testo", "{{es-noun|m|f=testa|f2=test2a|f3=test3a}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa", "test2a", "test3a"], "fpl":["testas", "test2as", "test3as"]}

    word = make_word("testo", "{{es-noun|m|f=testa|f2=test2a|f3=test3a|fpl=testaz}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa", "test2a", "test3a"], "fpl":["testaz"]}

    word = make_word("testo", "{{es-noun|m|f=testa|f2=test2a|f3=test3a|fpl=testaz|fpl2=test2az}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa", "test2a", "test3a"], "fpl":["testaz", "test2az"]}

    word = make_word("argentine", "{{es-noun|m|g2=f|m=argentino|f=argentina}}")
    assert Data.get_forms(word) == {"pl":["argentines"], "m":["argentino"], "mpl":["argentinos"], "f":["argentina"], "fpl":["argentinas"]}

def test_get_verb_forms1():

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
    forms = Data.get_forms(word)
    assert forms == {'1': ['tener'], '2': ['teniendo'], '3': ['tenido'], '4': ['tenida'], '5': ['tenidos'], '6': ['tenidas'], '7': ['tengo'], '8': ['tienes'], '9': ['tenés'], '10': ['tiene'], '11': ['tenemos'], '12': ['tenéis'], '13': ['tienen'], '14': ['tenía'], '15': ['tenías'], '16': ['tenía'], '17': ['teníamos'], '18': ['teníais'], '19': ['tenían'], '20': ['tuve'], '21': ['tuviste'], '22': ['tuvo'], '23': ['tuvimos'], '24': ['tuvisteis'], '25': ['tuvieron'], '26': ['tendré'], '27': ['tendrás'], '28': ['tendrá'], '29': ['tendremos'], '30': ['tendréis'], '31': ['tendrán'], '32': ['tendría'], '33': ['tendrías'], '34': ['tendría'], '35': ['tendríamos'], '36': ['tendríais'], '37': ['tendrían'], '38': ['tenga'], '39': ['tengas'], '41': ['tenga'], '42': ['tengamos'], '43': ['tengáis'], '44': ['tengan'], '45': ['tuviera'], '46': ['tuvieras'], '47': ['tuviera'], '48': ['tuviéramos'], '49': ['tuvierais'], '50': ['tuvieran'], '51': ['tuviese'], '52': ['tuvieses'], '53': ['tuviese'], '54': ['tuviésemos'], '55': ['tuvieseis'], '56': ['tuviesen'], '57': ['tuviere'], '58': ['tuvieres'], '59': ['tuviere'], '60': ['tuviéremos'], '61': ['tuviereis'], '62': ['tuvieren'], '63': ['ten'], '64': ['tené'], '65': ['tenga'], '66': ['tengamos'], '67': ['tened'], '68': ['tengan'], '69': ['tengas'], '70': ['tenga'], '71': ['tengamos'], '72': ['tengáis'], '73': ['tengan']}

def test_get_verb_forms2():

    data = """\
==Spanish==

===Etymology 1===
From {{der|es|la|attentō}}.

====Verb====
{{es-verb|atent|ar|pres=atiento}}

# {{lb|es|intransitive}} to commit a violent or criminal [[attack]], to [[strike]]

===Etymology 2===
{{rfe|es}}

====Verb====
{{es-verb|atent|ar}}

# {{lb|es|transitive|obsolete}} to [[touch]]

===Conjugation===
{{es-conj-ar|at|nt|p=e-ie|combined=1}}
"""

    wikt = parse_page(data, "atentar", None)
    word = next(wikt.ifilter_words())
    template = next(word.ifilter_templates(matches=lambda x: "es-verb" in x.name.strip()))
    forms = Data.get_forms(word)
    assert len(forms) == 73
