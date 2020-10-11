#!/usr/bin/python3
# -*- python-mode -*-

import requests
import json
import urllib

def expand_template(data):
    url = 'https://en.wiktionary.org/w/api.php?action=expandtemplates&format=json&prop=wikitext&text=' + urllib.parse.quote(data)

    res = requests.get( url )
    json_data = res.json()
    return json.loads(json_data['expandtemplates']['wikitext'])

def main():
    data = expand_template("{{#invoke:User:DTLHS/languages|export_languages|en}}")

    shortdata = {}
    for k,v in data.items():
        if isinstance(v, dict):
            shortdata[k] = v["1"]
        else:
            shortdata[k] = v[0]

    print("languages =", json.dumps(shortdata, indent=4, sort_keys=True, ensure_ascii=False))

main()
