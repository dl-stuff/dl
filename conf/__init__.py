import json
import os

from core import Conf

ELEMENTS = ('flame', 'water', 'wind', 'light', 'shadow')
WEAPON_TYPES = ('sword', 'blade', 'dagger', 'axe', 'lance', 'bow', 'wand', 'staff')
ROOT_DIR = os.getenv('ROOT_DIR', os.path.realpath(os.path.join(__file__, '../..')))

def load_json(fn):
    froot = os.path.join(ROOT_DIR, 'conf')
    fpath = os.path.join(froot, fn)
    if not os.path.exists(fpath):
        fpath = os.path.join(froot, 'conf', fn)
    with open(fpath, 'r', encoding='utf8') as f:
        return json.load(f, parse_float=float, parse_int=int)

coability = load_json('chains.json')
skillshare = load_json('skillshare.json')
wyrmprints = load_json('wyrmprints.json')
weapons = load_json('weapons.json')

baseconfs = {}
for wep in WEAPON_TYPES:
    baseconfs[wep] = load_json(f'base/{wep}.json')

dragons = {}
for ele in ELEMENTS:
    dragons[ele] = load_json(f'drg/{ele}.json')

alias = {}
for target, alst in load_json('alias.json').items():
    for a in alst:
        alias[a] = target

elecoabs = {}
for ele in ELEMENTS:
    elecoabs[ele] = {**coability['all'], **coability[ele]}

advconfs = {}
def load_adv_json(adv):
    try:
        return advconfs[adv]
    except KeyError:
        aconf = load_json(f'adv/{adv}.json')
        advconfs[adv] = aconf
        return aconf

def get_icon(adv):
    return load_adv_json(adv)['c']['icon']

def get_adv(name):
    conf = Conf(load_adv_json(name))

    wt = conf.c.wt
    base = baseconfs[wt]
    conf.update(Conf(base), rebase=True)
    if bool(conf.c.spiral):
        conf.update(conf.lv2)
    del conf['lv2']

    return conf
