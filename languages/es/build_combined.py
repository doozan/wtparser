#!/usr/bin/python3

import luadata_to_python

import requests
import argparse
import datetime

def get_wikipage(page):
    url = 'https://en.wiktionary.org/w/api.php?action=query&prop=revisions&rvslots=*&rvprop=content|ids&format=json&titles=' + page
    niceurl = 'https://en.wiktionary.org/wiki/' + page

    res = requests.get( url )
    json_data = res.json()
    revision = list(json_data['query']['pages'].values())[0]['revisions'][0]['revid']
    wikitext = list(json_data['query']['pages'].values())[0]['revisions'][0]['slots']['main']['*']
    return { "wikitext": wikitext, "revision": revision, "url": niceurl }

def dump_page(page):

    res = get_wikipage(page)

    pydata = luadata_to_python.convert(res["wikitext"], "data", "_data", no_warning=True)

print(f"""\
# Data from: {res['url']} (revision: {res['revision']}, scraped {datetime.datetime.now()})
# This file is generated automatically, do not hand edit

def venir_imp_i2s(form):
    return form[:-1] + "nos"

def ir_imp_i2p_accent(form):
    return form[:-1] + "í"

def ir_im_i2p_idos(form):
    return "idos, iros"

"""
    print(pydata)


def main():
    parser = argparse.ArgumentParser(description='Scrape data from wiktionary page')
    parser.add_argument("page", help="page to download (eg. Template:es-conj)")
    args = parser.parse_args()

    dump_page(args.page)

main()
