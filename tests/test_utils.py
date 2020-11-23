from ..utils import template_aware_split, nest_aware_resplit

def test_template_aware_split():

    orig_text = "{{t|q1, q2}}"
    items = list(template_aware_split(",", orig_text))
    assert len(items) == 1
    assert items[0] == orig_text




# from utils import template_depth
#
# def test_template_depth():
#
#    assert template_depth(" {{ blah }} ") == 0
#    assert template_depth("blah}} {{ blah }} ") == 0
#    assert template_depth(" {{ blah }} {{blah") == 1


# d = Definition("es", "# [[word1]], [[word2]]; [[word3]]")
# assert d._template_depth == 0
# d.add(" }} {{ blah }}")
# assert d._template_depth == 0
# d.add(" {{test")
# assert d._template_depth == 1
# d.add(" }} {{ blah }}")
# assert d._template_depth == 0
# d.add(" {{test{{test2{{test3{{blah}}")
# assert d._template_depth == 3
# d.add("}} }} }}")
# assert d._template_depth == 0
# d.add("}} }} }}")
# assert d._template_depth == 0

def test_nest_aware_resplit():
    line = "{{blah|blah, blah}} blah, blah; blah / blah (blah,blah)"
    res = list(nest_aware_resplit(r"[\/,;]", line, [("{{","}}"), ("(", ")")]))
    assert res == [("{{blah|blah, blah}} blah", ","), (" blah", ";"), (" blah ", "/"), (" blah (blah,blah)", "")]

    line = "blah, blah; blah / blah"
    res = list(nest_aware_resplit(r"([\/,;])", line, [("{{","}}"), ("(", ")")]))
    assert res == [("blah", ","), (" blah", ";"), (" blah ", "/"), (" blah", "")]

    line = "blah, blah"
    res = list(nest_aware_resplit(r"([\/,;])", line, [("{{","}}"), ("(", ")")]))
    assert res == [("blah", ","), (" blah", "")]

    line = "* {{sense|sense1}} {{l|es|syn1}}, {{l|es|syn2}}\n"
    res = list(nest_aware_resplit(r"([\/,;])", line, [("{{","}}"), ("(", ")")]))
    assert res == [('* {{sense|sense1}} {{l|es|syn1}}', ','), (' {{l|es|syn2}}\n', '')]

    line = "blah (blah"
    res = list(nest_aware_resplit(r"([\/,;])", line, [("{{","}}"), ("(", ")")]))
    assert res == [("blah (blah", "")]

    line = "blah, blah"
    res = list(nest_aware_resplit(r"([\/,;])", line, [("{{","}}"), ("(", ")")]))
    for text, delim in res:
        print(f"text '{text}'")
        print(f"delim '{delim}'")


