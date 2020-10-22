from core.advbase import *

class Hunter_Sarisse(Adv):
    comment = '8hit FS on A&O sized enemy (see special for 20hit); needs combo time to keep combo'
    # conf = {'attenuation.hits': 0}

class Hunter_Sarisse_ALL(Hunter_Sarisse):
    comment = '20hit FS'
    conf = {'attenuation.hits': -1}

variants = {
    None: Hunter_Sarisse,
    'ALL': Hunter_Sarisse_ALL
}
