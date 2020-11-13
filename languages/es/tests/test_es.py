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

    # es-adj-sup works, too
    word = make_word("testo", "{{es-adj-sup|f=testa}}")
    assert Data.get_forms(word) == {"pl":["testos"], "f":["testa"], "fpl":["testas"]}


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
    assert forms['1'] == {'tener'}
    assert forms['2'] == {'teniendo'}
    assert forms['inf_acc_1'] == {'tenerme'}
    assert sorted(forms['inf_acc-dat_1']) == sorted(['tenérmelos', 'tenérmela', 'tenérmelas', 'tenérmelo'])

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
    assert len(forms) == 188

def test_get_verb_rogar():

    data = """\
==Spanish==

===Verb===
{{es-verb|rog|ar|pres=ruego|pret=rogué}}

# to [[beg]], [[entreat]], [[implore]], [[pray]]

====Conjugation====
{{es-conj-ar|p=-gar o-ue|r|combined=1}}
"""

    wikt = parse_page(data, "rogar", None)
    word = next(wikt.ifilter_words())
    template = next(word.ifilter_templates(matches=lambda x: "es-verb" in x.name.strip()))
    forms = Data.get_forms(word)

    assert forms["1"] == {"rogar"}


def test_get_verb_forms_noconjugation():

    data = """\
==Spanish==

===Verb===
{{es-verb|atent|ar|pres=atiento}}

# {{lb|es|intransitive}} to commit a violent or criminal [[attack]], to [[strike]]
"""

    wikt = parse_page(data, "atentar", None)
    word = next(wikt.ifilter_words())
    template = next(word.ifilter_templates(matches=lambda x: "es-verb" in x.name.strip()))
    forms = Data.get_forms(word)
    assert forms == {}


def test_inflect():
    assert len(Data.inflect(["habl"], "-ar", "", False)) == 73
    assert Data.inflect(["habl"], "-ar", "", False)[1] == ["hablar"]
    assert Data.inflect(["habl"], "-ar", "", True)[1] == ["hablarse"]

def test_inflect_combined():
    forms = Data.inflect(["habl"], "-ar", "", False)
    combined = Data.inflect_combined(forms, "-ar", "", False)
    assert  combined == {'inf_acc_1': ['hablarme'], 'inf_acc_2': ['hablarte'], 'inf_acc_3': ['hablarlo', 'hablarla', 'hablarse'], 'inf_acc_4': ['hablarnos'], 'inf_acc_5': ['hablaros'], 'inf_acc_6': ['hablarlos', 'hablarlas', 'hablarse'], 'inf_acc_7': ['hablarse'], 'inf_dat_1': ['hablarme'], 'inf_dat_2': ['hablarte'], 'inf_dat_3': ['hablarle', 'hablarse'], 'inf_dat_4': ['hablarnos'], 'inf_dat_5': ['hablaros'], 'inf_dat_6': ['hablarles', 'hablarse'], 'ger_acc_1': ['hablándome'], 'ger_acc_2': ['hablándote'], 'ger_acc_3': ['hablándolo', 'hablándola', 'hablándose'], 'ger_acc_4': ['hablándonos'], 'ger_acc_5': ['hablándoos'], 'ger_acc_6': ['hablándolos', 'hablándolas', 'hablándose'], 'ger_acc_7': ['hablándose'], 'ger_dat_1': ['hablándome'], 'ger_dat_2': ['hablándote'], 'ger_dat_3': ['hablándole', 'hablándose'], 'ger_dat_4': ['hablándonos'], 'ger_dat_5': ['hablándoos'], 'ger_dat_6': ['hablándoles', 'hablándose'], 'imp_i2s_acc_1': ['háblame'], 'imp_i2s_acc_2': ['háblate'], 'imp_i2s_acc_3': ['háblalo', 'háblala'], 'imp_i2s_acc_4': ['háblanos'], 'imp_i2s_acc_6': ['háblalos', 'háblalas'], 'imp_i2s_dat_1': ['háblame'], 'imp_i2s_dat_2': ['háblate'], 'imp_i2s_dat_3': ['háblale'], 'imp_i2s_dat_4': ['háblanos'], 'imp_i2s_dat_6': ['háblales'], 'imp_f2s_acc_1': ['hábleme'], 'imp_f2s_acc_3': ['háblelo', 'háblela', 'háblese'], 'imp_f2s_acc_4': ['háblenos'], 'imp_f2s_acc_6': ['háblelos', 'háblelas'], 'imp_f2s_acc_7': ['háblese'], 'imp_f2s_dat_1': ['hábleme'], 'imp_f2s_dat_3': ['háblele', 'háblese'], 'imp_f2s_dat_4': ['háblenos'], 'imp_f2s_dat_6': ['hábleles'], 'imp_1p_acc_2': ['hablémoste'], 'imp_1p_acc_3': ['hablémoslo', 'hablémosla'], 'imp_1p_acc_4': ['hablémonos'], 'imp_1p_acc_5': ['hablémoos'], 'imp_1p_acc_6': ['hablémoslos', 'hablémoslas'], 'imp_1p_dat_2': ['hablémoste'], 'imp_1p_dat_3': ['hablémosle'], 'imp_1p_dat_4': ['hablémonos'], 'imp_1p_dat_5': ['hablémoos'], 'imp_1p_dat_6': ['hablémosles'], 'imp_i2p_acc_1': ['habladme'], 'imp_i2p_acc_3': ['habladlo', 'habladla'], 'imp_i2p_acc_4': ['habladnos'], 'imp_i2p_acc_5': ['hablaos'], 'imp_i2p_acc_6': ['habladlos', 'habladlas'], 'imp_i2p_acc_7': ['hablados'], 'imp_i2p_dat_1': ['habladme'], 'imp_i2p_dat_3': ['habladle'], 'imp_i2p_dat_4': ['habladnos'], 'imp_i2p_dat_5': ['hablaos'], 'imp_i2p_dat_6': ['habladles'], 'imp_f2p_acc_1': ['háblenme'], 'imp_f2p_acc_3': ['háblenlo', 'háblenla'], 'imp_f2p_acc_4': ['háblennos'], 'imp_f2p_acc_6': ['háblenlos', 'háblenlas', 'háblense'], 'imp_f2p_acc_7': ['háblense'], 'imp_f2p_dat_1': ['háblenme'], 'imp_f2p_dat_3': ['háblenle'], 'imp_f2p_dat_4': ['háblennos'], 'imp_f2p_dat_6': ['háblenles', 'háblense']}

    forms = Data.inflect([], "-ir", "venir", False)
    combined = Data.inflect_combined(forms, "-ir", "venir", False)
    assert combined['imp_i2s_acc_4'] == ['venos']
    assert combined['imp_i2s_dat_4'] == ['venos']
    assert combined['imp_i2p_acc_5'] == ['veníos']
    assert combined['imp_i2p_dat_5'] == ['veníos']

    forms = Data.inflect([], "-ir", "ir", False)
    combined = Data.inflect_combined(forms, "-ir", "ir", False)
    assert combined['imp_i2p_dat_5'] ==  ['idos', 'iros']


def test_create_accented_form():
    assert Data.create_accented_form("hablame") == "háblame"

    # 'ue' or 'ua' count as 1 vowel, accent goes on e or a
    assert Data.create_accented_form("aburguesele") == "aburguésele"
    assert Data.create_accented_form("malualo") == "málualo"
    # unless ua_disyllabic is set
    assert Data.create_accented_form("malualo",True) == "malúalo"

    # 'ai' or 'oi' counts as 1 vowel, accent goes on a or o
    assert Data.create_accented_form("bailame") == "báilame"
    assert Data.create_accented_form("boilame") == "bóilame"
    assert Data.create_accented_form("beilame") == "beílame"

