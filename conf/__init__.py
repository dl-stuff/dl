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

coability = load_json('chains.json')
skillshare = load_json('skillshare.json')
wyrmprints = load_json('wyrmprints.json')
weapons = load_json('weapons.json')

advconfs = {}
def load_adv_json(adv):
    try:
        return advconfs[adv]
    except KeyError:
        aconf = load_json(f'adv/{adv}.json')
        advconfs[adv] = aconf
        return aconf

baseconfs = {}
def load_base_json(wep):
    try:
        return baseconfs[wep]
    except KeyError:
        aconf = load_json(f'base/{wep}.json')
        baseconfs[wep] = aconf
        return aconf

drgconfs = {}
def load_drg_json(ele):
    try:
        return drgconfs[ele]
    except KeyError:
        aconf = load_json(f'drg/{ele}.json')
        drgconfs[ele] = aconf
        return aconf

alias = {}
for target, alst in load_json('alias.json').items():
    for a in alst:
        alias[a] = target

elecoabs = {}
def coability_dict(ele):
    if ele:
        try:
            return elecoabs[ele]
        except:
            cdict = {**coability['all'], **coability[ele]}
            elecoabs[ele] = cdict
            return cdict
    else:
        return coability['all'].copy()

def get_adv(name):
    conf = Conf(load_adv_json(name))

    wt = conf.c.wt
    base = load_base_json(wt)
    conf.update(Conf(base), rebase=True)
    if bool(conf.c.spiral):
        conf.update(conf.lv2)
    del conf['lv2']

    return conf
