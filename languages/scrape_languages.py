#!/usr/bin/python3
# -*- python-mode -*-

import csv
import json
import requests
import urllib

def expand_template(data):
    url = 'https://en.wiktionary.org/w/api.php?action=expandtemplates&format=json&prop=wikitext&text=' + urllib.parse.quote(data)

    res = requests.get( url )
    json_data = res.json()
    return json_data['expandtemplates']['wikitext']

def main():
    #data = expand_template("{{#invoke:User:DTLHS/languages|export_languages|en}}")
    data = expand_template("{{#invoke:list of languages, csv format|show}}")

    lines = [line for line in data.splitlines() if line and not line.startswith("<pre")]
    csvreader = csv.DictReader(lines, delimiter=';')

#    line;code;canonical name;category;type;family code;family;sortkey?;autodetect?;exceptional?;script codes;other names;standard characters

    shortdata = {r["code"]: r["canonical name"] for r in csvreader}

    print("languages =", json.dumps(shortdata, indent=4, sort_keys=True, ensure_ascii=False))

main()
