from ..utils import template_aware_split, nest_aware_resplit, wiki_search

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



def test_wikisearch_basic1():
    text = """\
START
  blah1
END

START
  blah2
END

START
  blah3
START
  blah4
END

END

START
  blah5
"""

    res = wiki_search(text, "START")
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END', ''], ['START', '  blah2', 'END', ''], ['START', '  blah3'], ['START', '  blah4', 'END', '', 'END', ''], ['START', '  blah5']]

    res = wiki_search(text, "START", "END", False)
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END'], ['START', '  blah2', 'END'], ['START', '  blah3'], ['START', '  blah4', 'END'], ['START', '  blah5']]

    res = wiki_search(text, "START", "END", True)
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END'], ['START', '  blah2', 'END'], ['START', '  blah3', 'START', '  blah4', 'END']]


def test_wikisearch_ignore_templates():
    text = """\
START
  blah1
END
{{template|
START
  blah2
END
}}
"""

    res = wiki_search(text, "START", "END")
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END']]

    res = wiki_search(text, "START", "END", ignore_templates=True)
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END'], ['START', '  blah2', 'END']]


def test_wikisearch_ignore_nowiki():
    text = """\
START
  blah1
END
<nowiki>
START
  blah2
END
</nowiki>
"""

    res = wiki_search(text, "START", "END", ignore_nowiki=False)
    res = list(map(str.splitlines,res))
    print(res)

    res = wiki_search(text, "START", "END", ignore_nowiki=True)
    res = list(map(str.splitlines,res))
    print(res)


def test_wikisearch_ignore_comments():
    text = """\
<!-- comment -->
START
  blah1
END
<!--
START
  blah2
END
-->
<!--START
blah3
END-->
"""

    res = wiki_search(text, "START", "END")
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END']]

    res = wiki_search(text, "START", "END", ignore_comments=True)
    res = list(map(str.splitlines,res))
    print(res)
    assert res == [['START', '  blah1', 'END'], ['START', '  blah2', 'END'], ['START', 'blah3', 'END']]


def test_wikisearch_ignore_nested():
    text = """\
START
  blah1
END
{{template|
<nowiki>
START
  blah2
END
</nowiki>
}}
"""

    res = wiki_search(text, "START", "END")
    res = list(map(str.splitlines,res))
    assert res == [['START', '  blah1', 'END']]

    res = wiki_search(text, "START", "END", ignore_nowiki=True)
    res = list(map(str.splitlines,res))
    assert res == [['START', '  blah1', 'END']]

    res = wiki_search(text, "START", "END", ignore_templates=True)
    res = list(map(str.splitlines,res))
    assert res == [['START', '  blah1', 'END']]

    res = wiki_search(text, "START", "END", ignore_nowiki=True, ignore_templates=True)
    res = list(map(str.splitlines,res))
    assert res == [['START', '  blah1', 'END'], ['START', '  blah2', 'END']]

def test_wikisearch_veggie():

    text = """\
before
pre {{trans-top}} post
blah
{{trans-mid}}
pre {{trans-bottom}} post
after
"""

    TOP_TEMPLATES = ("trans-top", "trans-top-see", "trans-top-also", "checktrans-top", "ttbc-top")
    BOTTOM_TEMPLATES = ("checktrans-bottom", "trans-bottom", "ttbc-bottom")
    SKIP_LINES = ["{{trans-mid}}"]
    RE_TOP_TEMPLATES = "|".join(TOP_TEMPLATES)
    RE_BOTTOM_TEMPLATES = "|".join(BOTTOM_TEMPLATES)


    res = wiki_search(text,
                fr"^.*{{{{\s*({RE_TOP_TEMPLATES})",
                fr"{{{{\s*({RE_BOTTOM_TEMPLATES})\s*}}}}.*$",
                end_required=False,
                ignore_templates=True,
                ignore_nowiki=True,
            )

    res = list(map(str.splitlines,res))
    assert res == [['pre {{trans-top}} post', 'blah', '{{trans-mid}}', 'pre {{trans-bottom}} post']]


