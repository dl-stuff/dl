import json
import os

from slot import Slots
from core import Conf

import wep
import conf.halidom

def load_json(fn):
    froot = os.path.dirname(os.path.realpath('__file__'))
    fpath = os.path.join(froot, fn)
    if not os.path.exists(fpath):
        fpath = os.path.join(froot, 'conf', fn)
    with open(fpath, 'r', encoding='utf8') as f:
        return json.load(f, parse_float=float, parse_int=int)

# advconfs = load_json('advconf.json')
advconfs = {}
def load_adv_json(adv):
    return advconfs.get(adv, load_json(f'adv/{adv}.json'))

coability = load_json('chains.json')
skillshare = load_json('skillshare.json')

wepconfs = {}
def load_wep_json(wep):
    return wepconfs.get(wep, load_json(f'wep/{wep}.json'))

def coability_dict(ele):
    if ele:
        return {**coability['all'], **coability[ele]}
    else:
        return coability['all'].copy()


def get(name):
    conf = Conf(load_adv_json(name))
    wt = conf.c.wt

    # weapon = getattr(wep, wt)
    # conf.update(Conf(weapon.conf))
    # if bool(conf.c.spiral):
    #     conf.update(Conf(weapon.lv2))

    wepconf = load_wep_json(wt)
    conf.update(Conf(wepconf), rebase=True)
    if bool(conf.c.spiral):
        conf.update(conf.lv2)
    del conf['lv2']

    return conf
