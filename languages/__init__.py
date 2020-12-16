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

__all__ = ["es"]

import re

class LanguageData():
    headwords = {}
    gender_sources = {
        "head": {
            "g": ["g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
      },
    }

    @classmethod
    def match_headword(cls, template):
        return str(template.name) in cls.headwords

    @classmethod
    def get_gender_and_number(cls, word):
        """ Returns an array of gender-number values
        See https://en.wiktionary.org/wiki/Module:gender_and_number for details
        """

        template = word.headword
        if template is None:
            return None

        sources = cls.gender_sources.get(str(template.name))
        if not sources:
            return []

        res = {}
        for k,params in sources.items():
            for param in params:
                if template.has(param):
                    res[k] = res.get(k, []) + [str(template.get(param).value)]

        return [ v[0] for v in res.values() ]

    @classmethod
    def get_forms(cls, word):
        template = word.headword
        if template is None:
            return None

        if str(template.name) == "head":
            return cls.get_head_forms(word)

    @classmethod
    def get_head_forms(cls, word):
        template = word.headword
        if template is None:
            return {}

        params = cls.get_template_params(template)

        res = {}
        offset=3
        while str(offset+1) in params:
            formtype = params[str(offset)]
            form = params[str(offset+1)]
            offset += 2

            if not form.strip():
                continue

            if formtype not in res:
                res[formtype] = [form]
            else:
                res[formtype].append(form)

        return res

    @staticmethod
    def get_template_params(template):
        params = {}
        param_lists = {}
        for param in template.params:
            name = str(param.name).strip()
            value = str(param.value).strip()

            res = re.match(r"([^0-9]+?)[1-9]+$", str(param.name))
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

