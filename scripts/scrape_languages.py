#!/usr/bin/python3
# -*- python-mode -*-

import csv
import json
import requests
import sys
import urllib

from collections import defaultdict

def expand_template(data):
    url = 'https://en.wiktionary.org/w/api.php?action=expandtemplates&format=json&prop=wikitext&text=' + urllib.parse.quote(data)

    res = requests.get( url )
    json_data = res.json()
    return json_data['expandtemplates']['wikitext']

def main():
    #data = expand_template("{{#invoke:User:DTLHS/languages|export_languages|en}}")
    data = expand_template("{{#invoke:list of languages, csv format|show}}")
    lines = [line for line in data.splitlines() if line and not line.startswith("<pre")]

    #with open("lang.data") as infile:
    #    lines = [line for line in infile if line and not line.startswith("<pre")]

    csvreader = csv.DictReader(lines, delimiter=';')
    data = {r["code"]: r["canonical name"] for r in csvreader}
    len_all_lang_ids = len(data)
    print("ALL_LANG_IDS =", json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))

    csvreader = csv.DictReader(lines, delimiter=';')
    data = {r["canonical name"]: r["code"] for r in csvreader}
    len_all_langs = len(data)
    print("ALL_LANGS =", json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))

    assert len_all_langs == len_all_lang_ids

#    line;code;canonical name;category;type;family code;family;sortkey?;autodetect?;exceptional?;script codes;other names;standard characters

    csvreader = csv.DictReader(lines, delimiter=';')
    data = defaultdict(list)
    for r in csvreader:
        for alt_name in r["other names"].split(","):
            if not alt_name:
                continue
            if alt_name in data:
                print(f"{alt_name} is an alt_name of {r['canonical name']} and {data[alt_name]}", file=sys.stderr)
            data[alt_name].append(r['canonical name'])
    print("ALT_LANGS =", json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))

main()