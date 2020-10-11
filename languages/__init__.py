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

class LanguageData():
    headwords = {}
    gender_sources = {
        "head": {
            "g": ["g", "gen", "g1"],
            "g2": ["g2"],
            "g3": ["g3"],
      },
    }

    form_sources = {
    #    "es-adj": {
    #        "m": ["m"],
    #        "f": ["f", "f2", "f3"],
    #        "pl": ["pl", "pl2", "pl3"],
    #        "mpl": ["mpl", "mpl2", "mpl2"],
    #        "fpl": ["fpl", "fpl2", "mpl3"]
    #    },
    }

    @classmethod
    def match_headword(cls, template):
        return str(template.name) in cls.headwords

    @classmethod
    def get_genders(cls, template):
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
    def get_forms(cls, template, title):
        sources = cls.form_sources.get(str(template.name))
        if not sources:
            return None

        res = {}
        for k,params in sources.items():
            for param in params:
                if template.has(param):
                    res[k] = res.get(k, []) + [str(template.get(param).value).strip()]

        return res
