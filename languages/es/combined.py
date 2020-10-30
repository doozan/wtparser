# Data from: https://en.wiktionary.org/wiki/Module:es-conj/data/combined (revision: 51641465, scraped 2020-10-29 15:25:30.792520)
# This file is generated automatically, do not hand edit
#

def venir_imp_i2s(form):
    return form[:-1] + "nos"

def ir_imp_i2p_accent(form):
    return form[:-1] + "í"

def ir_im_i2p_idos(form):
    return "idos, iros"

_data = {

"inf": {
          "index": 1,
          "accented_stem": False,
          "stem_cuts": {},
          "ending_irregularities": {},
          "paradigm_irregularities": {},
          "paradigm_no_accent":  {},
          "ua_disyllabic": {},
          "dat":    [["me"], ["te"],  ["le", "se"],     ["nos"], ["os"],  ["les", "se"]],
          "acc": [["me"], ["te"], ["lo", "la", "se"], ["nos"], ["os"], ["los", "las", "se"], ["se"]]
},

"ger": {
          "index": 2,
          "accented_stem": True,
          "stem_cuts": {},
          "ending_irregularities": {},
          "paradigm_irregularities": {},
          "paradigm_no_accent": {},
          "ua_disyllabic": {},
          "dat":    [["me"], ["te"], ["le", "se"],      ["nos"], ["os"],   ["les", "se"]],
          "acc": [["me"], ["te"], ["lo", "la", "se"], ["nos"], ["os",], ["los", "las", "se"], ["se"]]
},


"imp_i2s": {
          "index": 63,
          "accented_stem": True,
          "stem_cuts": {},
          "ending_irregularities": {},
          "paradigm_no_accent": {  "-tener": True,   "-venir": True,   "hacer i-í": True,
              "-poner": True,   "ver e-é":  True,   "estar": True
        },
          "ua_disyllabic": {  "u-ú": True},
          "paradigm_irregularities": {  "venir": [["dat", 4, "nos", venir_imp_i2s], ["acc", 4, "nos", venir_imp_i2s]],
                                         "-venir": [["dat", 4, "nos", venir_imp_i2s], ["acc", 4, "nos", venir_imp_i2s]],
                                         "salir": [["dat", 4, "le", "sal-le"]]},
          "dat":    [["me"], ["te"], ["le"],       ["nos"], {}, ["les"]],
          "acc": [["me"], ["te"], ["lo", "la"], ["nos"], {}, ["los", "las"]]
},

"imp_f2s": {
          "index": 65,
          "accented_stem": True,
          "stem_cuts": {},
          "ending_irregularities": {},
          "paradigm_irregularities": {},
          "paradigm_no_accent": {},
          "ua_disyllabic": {},
          "dat":    [["me"], {}, ["le", "se"],       ["nos"], {}, ["les"]],
          "acc": [["me"], {}, ["lo", "la", "se"], ["nos"], {}, ["los", "las"], ["se"]]
},

"imp_1p": {
          "index": 66,
          "accented_stem": True,
          "stem_cuts": {  4: [1,-2],   5: ["os",1,-2]},
          "ending_irregularities": {},
          "paradigm_irregularities": {},
          "paradigm_no_accent": {},
          "ua_disyllabic": {},
          "dat":    [{}, ["te"], ["le"],       ["nos"], ["os"], ["les"]],
          "acc": [{}, ["te"], ["lo", "la"], ["nos"], ["os"], ["los", "las"]]
},



"imp_i2p": {
          "index": 67,
          "accented_stem": False,
          "stem_cuts": {  5: ["os",1,-2]},
          "paradigm_no_accent": {},
          "ua_disyllabic": {},
          "ending_irregularities": {  "-ir": [["dat", 5, "os", ir_imp_i2p_accent], ["acc", 5, "os", ir_imp_i2p_accent]]},
          "paradigm_irregularities": {  "ir": [["dat", 5, "os", ir_im_i2p_idos], ["acc", 5, "os", ir_im_i2p_idos]]},
          "dat":    [["me"], {}, ["le"],       ["nos"], ["os"], ["les"]],
          "acc": [["me"], {}, ["lo", "la"], ["nos"], ["os"], ["los", "las"], ["os"]]
},

"imp_f2p": {
          "index": 68,
          "accented_stem": True,
          "stem_cuts": {},
          "paradigm_no_accent": {},
          "ending_irregularities": {},
          "paradigm_irregularities": {},
          "ua_disyllabic": {},
          "dat":    [["me"], {}, ["le"],       ["nos"], {},  ["les", "se"]],
          "acc": [["me"], {}, ["lo", "la"], ["nos"], {}, ["los", "las", "se"], ["se"]]
},

}
