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

"""
Data and utilities for processing Spanish sections of enwiktionary
"""

import re
import sys

from .paradigms import paradigms
from .. import LanguageData

class Data(LanguageData):

    headwords = {
        "es-adj",
        "es-adj-inv",
        "es-adv",
        "es-conjunction",
        "es-diacritical mark",
        "es-interj",
        "es-interjection",
        "es-letter",
        "es-noun",
        "es-past participle",
        "es-phrase",
        "es-prefix",
        "es-proverb",
        "es-proper noun",
        "es-punctuation mark",
        "es-suffix",
        "es-verb"
    }

    gender_sources = {
        "head": {
            "g": ["g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "es-noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
        "es-proper noun": {
            "g": ["1", "g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
        },
    }

    form_sources = {
        "es-proper noun": {
            "m": ["m", "m2", "m3"],
            "f": ["f", "f2", "f3"],
            "pl": ["pl", "pl2", "pl3"],
            "mpl": ["mpl", "mpl2", "mpl2"],
            "fpl": ["fpl", "fpl2", "mpl3"]
        },
    }

    _unstresstab = str.maketrans("áéíóú", "aeiou")
    _stresstab = str.maketrans("aeiou", "áéíóú")

    @classmethod
    def unstress(cls, word):
        return word.translate(cls._unstresstab)

    @classmethod
    def stress(cls, word):
        return word.translate(cls._stresstab)

    @classmethod
    def get_forms(cls, word):
        template = word.headword
        if template is None:
            return {}

        if str(template.name) == "es-noun":
            return cls.get_noun_forms(word)

        elif str(template.name) == "es-adj":
            return cls.get_adjective_forms(word)

        elif str(template.name) == "es-verb":
            return cls.get_verb_forms(word)

        return super().get_forms(word)


    @classmethod
    def get_adjective_forms(cls, word):
        template = word.headword
        if template is None:
            return {}

        title = word.page_title
        if not title:
            return {}

        params = cls.get_template_params(template)
        for k in [ "f", "pl", "mpl", "fpl" ]:
            if isinstance(params.get(k), str):
                params[k] = [params[k]]

        if "f" in params and "fpl" not in params:
            if "pl" in params:
                params["fpl"] = [ params["pl"][0] ]
            else:
                params["fpl"] = [ params["f"][0] + "s" ]

        if "m" not in params and "mpl" in params and "pl" not in params:
            params["pl"] = params.pop("mpl")

        if "pl" not in params:
            params["pl"] = [ title + "s" ]

        return {k:params[k] for k in ["f", "pl","fpl"] if k in params}

    @staticmethod
    def get_template_params(template):
        params = {}
        param_lists = {}
        for param in template.params:
            name = str(param.name).strip()
            value = str(param.value).strip()

            res = re.match(r"(.+?)[1-9]+$", str(param.name))
            if res:
                k = res.group(1)
                if k not in param_lists:
                    if k in params:
                        param_lists[k] = [params[k], value]
                    else:
                        param_lists[k] = [value]
                else:
                    param_lists[k].append(value)
            else:
                params[name] = value

        return {**params, **param_lists}


    @classmethod
    # This is a loose interpretation of Module:es-headword
    def get_noun_forms(cls, word):
        template = word.headword
        if template is None:
            return {}

        title = word.page_title
        if not title:
            return {}

        params = cls.get_template_params(template)
        # convert params that can be lists or a single value to lists
        for k in [ "f", "m", "pl", "mpl", "fpl" ]:
            if isinstance(params.get(k), str):
                params[k] = [params[k]]

        gender = "m"
        for k in ["1","g","gen"]:
            if k in params:
                if isinstance(params[k], str):
                    gender = params[k].replace("-","")
                else:
                    gender = params[k][0].replace("-","")

        genders = []
        if gender == "mf":
            genders = ["m", "mf"]
        elif gender == "mfp":
            genders = ["mp", "fp"]
        else:
            genders = [gender]

        plurals = []
        # Generate the default plural, if needed
        if genders[0] in ["m","f"]:
            # If "2" is empty, generate the default
            if "2" not in params or params["2"].strip() == "":
                plural = cls.make_plural_noun(title, gender)
                if plural:
                    plurals = plural

            # the "2" param is really a plural, put it at the head of the "pl" list
            elif "2" in params:
                plurals = [params["2"]]

            if "pl" in params:
                if isinstance(params["pl"], str):
                    plurals.append(params["pl"])
                else:
                    plurals += params["pl"]

        feminines = []
        feminine_plurals = []
        for f in params.get("f",[]):
            if f in ["1","+"]:
                forms = cls.adjective_forms(title, "m")
                f = forms["fs"] if forms else None
            if f:
                feminines.append(f)
                plural = cls.make_plural_noun(f, "f")
                if plural:
                    feminine_plurals += plural


        masculines = []
        masculine_plurals = []
        for m in params.get("m",[]):
            if m in ["1","+"]:
                forms = cls.adjective_forms(title, "m")
                m = forms["ms"] if forms else None
            if m:
                masculines.append(m)
                plural = cls.make_plural_noun(m, "m")
                if plural:
                    masculine_plurals += plural

        if "fpl" in params:
            feminine_plurals = params["fpl"]
        if "mpl" in params:
            masculine_plurals = params["mpl"]

        results = {}
        if feminines:
            results["f"] = list(dict.fromkeys(feminines))
        if masculines:
            results["m"] = list(dict.fromkeys(masculines))

        iters = [
            ("fpl", feminine_plurals, "f"),
            ("mpl", masculine_plurals, "m"),
        ]
        if genders[0] in ["m","f"]:
            iters.insert(0, ("pl", plurals, genders[0]))

        # Expand any default plurals (may result in more than one item)
        for target, plurals, gender in iters:
            expanded_plurals = []
            for plural in plurals:
                if plural is None or plural in ["1", "+"]:
                    expanded_plurals += cls.make_plural_noun(title, gender)
                else:
                    expanded_plurals.append(plural)

            for plural in expanded_plurals:
                if plural in ["?", "!", "~", "-"]: # No plural
                    plural = None

                if plural:
                    if target not in results:
                        results[target] = [plural]
                    elif plural not in results[target]:
                        results[target].append(plural)

        return results

    # This is a bug-for-bug implementation of wiktionary Module:es-headword make_plural_noun
    @classmethod
    def make_plural_noun(cls, singular, gender):
        if not singular:
            return []

        singular = singular.strip()
        if not singular:
            return []

        if " " in singular:
            res = re.match(
                "^(.+)( (?:de|a)l? .+)$", singular
            )  # match xxx (de|del|a|al) yyyy
            if res:
                pl = cls.make_plural_noun(res.group(1), gender)
                if not pl:
                    return []
                first = pl[0]
                second = res.group(2)
                return [first + second]
            else:
                words = singular.split(" ")
                if len(words) == 2:
                    pl = cls.make_plural_noun(words[0], gender)
                    if not pl:
                        return []
                    noun = pl[0]
                    adj = cls.adjective_forms(words[1], gender)
                    if not adj:
                        # raise ValueError("No adjective forms for", words[1], gender)
                        return []

                    if gender == "m" and "mp" in adj:
                        return [noun + " " + adj["mp"]]
                    elif gender == "f" and "fp" in adj:
                        return [noun + " " + adj["fp"]]
            # Bug: Anything with two spaces that doesn't include "de/l" or "a/l" will fall through
            # and be handled as a singular noun

        # ends in unstressed vowel or á, é, ó (casa: casas)
        if singular[-1] in "aeiouáéó":
            return [singular + "s"]

        # ends in í or ú (bambú: [bambús, bambúes])
        if singular[-1] in "íú":
            return [singular + "s", singular + "es"]

        # ends in a vowel + z (nariz: narices)
        if len(singular) > 1 and singular[-2] in "aeiouáéó" and singular.endswith("z"):
            return [singular[:-1] + "ces"]

        # ends tz (hertz: hertz)
        if singular.endswith("tz"):
            return [singular]

        modsingle = re.sub("qu([ie])", r"k\1", singular)
        vowels = []
        for c in modsingle:
            if c in "aeiouáéíóú":
                vowels.append(c)

        # ends in s or x with more than 1 syllable, last syllable unstressed (saltamontes: saltamontes)
        if len(vowels) > 1 and singular[-1] in "sx":
            return [singular]

        # I can't find any places where this actually applies
        # ends in l, r, n, d, z, or j with 3 or more syllables, accented on third to last syllable
        if (
            len(vowels) > 2
            and singular[-1] in "lrndzj"
            and vowels[len(vowels) - 2] in "áéíóú"
        ):
            return [singular]

        # ends in a stressed vowel + consonant, remove the stress and add -es (ademán: ademanes)
        if (
            len(singular) > 1
            and singular[-2] in "áéíóú"
            and singular[-1] not in "aeiouáéíóú"
        ):
            return [singular[:-2] + cls.unstress(singular[-2:]) + "es"]

        # ends in an unaccented vowel + y, l, r, n, d, j, s, x (color: coleres)
        if len(singular) > 1 and singular[-2] in "aeiou" and singular[-1] in "ylrndjsx":
            # two or more vowels and ends with -n, add stress mark to plural  (desorden: desórdenes)
            if len(vowels) > 1 and singular[-1] == "n":
                res = re.match("^(.*)([aeiou])([^aeiou]*[aeiou][nl])$", modsingle)
                if res:
                    start = res.group(1)  # dólmen
                    vowel = res.group(2)
                    end = res.group(3)
                    modplural = start + cls.stress(vowel) + end + "es"
                    plural = re.sub("k", "qu", modplural)
                    return [plural]
            return [singular + "es"]

        # ends in a vowel+ch (extremely few cases) (coach: coaches)
        if len(singular) > 2 and singular.endswith("ch") and singular[-3] in "aeiou":
            return [singular + "es"]

        # this matches mostly loanwords and is usually wrong (confort: conforts)
        if (
            len(singular) > 1
            and singular[-2] in "bcdfghjklmnpqrstvwxyz"
            and singular[-1] in "bcdfghjklmnpqrstvwxyz"
        ):
            return [singular + "s"]

        # this seems to match only loanwords
        # ends in a vowel + consonant other than l, r, n, d, z, j, s, or x (robot: robots)
        if (
            len(singular) > 1
            and singular[-2] in "aeiou"
            and singular[-1] in "bcfghkmpqtvwy"
        ):
            return [singular + "s"]

        return []


    # This is a bug-for-bug implementation of wiktionary Module:es-headword adjective_forms
    @classmethod
    def adjective_forms(cls, singular, gender):
        if singular.endswith("dor") and gender == "m":
            return {
                "ms": singular,
                "mp": singular + "es",
                "fs": singular + "a",
                "fp": singular + "as",
            }

        if singular.endswith("dora") and gender == "f":
            stem = singular[:-1]
            return {"ms": stem, "mp": stem + "es", "fs": stem + "a", "fp": stem + "as"}

        # Bug: no apparent support for non-feminines that end in -a
        if singular[-1] == "o" or (singular[-1] == "a" and gender == "f"):
            stem = singular[:-1]
            return {
                "ms": stem + "o",
                "mp": stem + "os",
                "fs": stem + "a",
                "fp": stem + "as",
            }

        if singular[-1] == "e" or singular.endswith("ista"):
            plural = singular + "s"
            return {"ms": singular, "mp": plural, "fs": singular, "fp": plural}

        if singular[-1] == "z":
            plural = singular[:-1] + "ces"
            return {"ms": singular, "mp": plural, "fs": singular, "fp": plural}

        if singular[-1] == "l" or singular[-2:] in ["ar", "ón", "ún"]:
            plural = singular[:-2] + cls.unstress(singular[-2]) + singular[-1] + "es"
            return {"ms": singular, "mp": plural, "fs": singular, "fp": plural}

        if singular.endswith("or"):
            plural = singular + "es"
            return {"ms": singular, "mp": plural, "fs": singular, "fp": plural}

        if singular[-2:] in ["án", "és", "ín"]:
            stem = singular[:-2] + cls.unstress(singular[-2]) + singular[-1]
            return {"ms": singular, "mp": stem + "es", "fs": stem + "a", "fp": stem + "as"}

    @classmethod
    def get_verb_forms(cls, word):
        """
        Instead of putting conjugation patterns in the es-verb template, Spanish
        verbs have a separate "Conjugation" section with es-conj templates
        """
        if not word:
            return {}

        template = word.headword
        if template is None:
            return {}

        if not template.has(2) or not str(template.get(2)).strip():
            return {}
        ending = "-" + str(template.get(2)).strip()

        matcher = lambda x: callable(getattr(x, "filter_sections", None)) and \
                any(x.filter_sections(matches=lambda y: y.name.strip() == "Conjugation"))
        ancestor = word if matcher(word) else word.get_matching_ancestor(matcher)
        if not ancestor:
            print("No conjugations", word.page_title, file=sys.stderr)
            return {}

        all_forms = {}
        for conjugation in ancestor.ifilter_sections(matches=lambda x: x.name.strip() == "Conjugation"):
            for t in conjugation.ifilter_templates(matches=lambda x: x.name.strip().startswith("es-conj")):
                pattern = None
                if t.has("p"):
                    pattern = str(t.get("p").value)
                stems = [ str(p.value).strip() for p in t.params if str(p.name).isdigit() ]

                for formtype, forms in cls.do_conjugate(stems, ending, pattern).items():
                    formtype = str(formtype)
                    for form in forms:
                        if not form:
                            continue
                        if formtype not in all_forms:
                            all_forms[formtype] = [form]
                        elif form not in all_forms[formtype]:
                            all_forms[formtype].append(form)

        return all_forms

    @classmethod
    def do_conjugate(self, stems, ending, pattern):

        # This has to be a deep copy, since we're overwriting values
        data = {k:v for k, v in paradigms[ending]['']['patterns'].items()}

        # Layer pattern data over base data
        if pattern:
            pattern_data = paradigms[ending][pattern]

            if 'replacement' in pattern_data:
                for pk,pv in pattern_data['replacement'].items():
                    for dk,dv in data.items():
                        if dv:
                            data[dk] = dv.replace(str(pk), pv)

            for pk,pv in pattern_data['patterns'].items():
                if pv == '-':
                    data[pk] = None
                else:
                    data[pk] = pv

        for dk,dv in data.items():
            if dv:
                if len(stems):
                    for sk, sv in enumerate(stems,1):
                        dv = dv.replace(str(sk), sv)
                data[dk] = [ k.strip() for k in dv.split(',') ]
            else:
                data[dk] = [ None ]

        return data

