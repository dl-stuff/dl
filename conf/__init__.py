import json
from slot import Slots
from core import Conf

import wep
import conf.halidom


def load_json(name):
    fname = ''
    find = '/'
    if __file__.find('/') == -1:
        find = '\\'
        if __file__.find('\\') == -1:
            find = None
            fname = name
    if find:
        l = __file__.rfind(find)
        fname = __file__[:l] + find + name

    with open(fname, 'r', encoding='utf8') as f:
        return json.load(f, parse_float=float, parse_int=int)


advconfs = load_json('advconf.json')
coability = load_json('chains.json')
skillshare = load_json('skillshare.json')


def coability_dict(ele):
    if ele:
        return {**coability['all'], **coability[ele]}
    else:
        return coability['all'].copy()


def get(name):
    conf = Conf(advconfs.get(name))
    wt = conf.c.wt
    weapon = getattr(wep, wt)
    conf.update(Conf(weapon.conf))
    if bool(conf.c.lv2_autos):
        conf.update(Conf(weapon.lv2))
    return conf
