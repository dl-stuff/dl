from collections import defaultdict
import json
import os
import glob
import operator

from core import Conf
import functools
from ctypes import c_float


ELEMENTS = ("flame", "water", "wind", "light", "shadow")
WEAPON_TYPES = (
    "sword",
    "blade",
    "dagger",
    "axe",
    "lance",
    "bow",
    "wand",
    "staff",
    "gun",
)
AUTO_FSF = ("wand", "lance", "blade")
TRIBE_TYPES = (
    "thaumian",
    "physian",
    "demihuman",
    "therion",
    "undead",
    "demon",
    "human",
    "dragon",
)
DURATIONS = (180,)
ELE_AFFLICT = {
    "flame": ("burn", "scorchrend"),
    "water": ("frostbite",),  # sadness
    "wind": ("poison", "stormlash"),
    "light": ("paralysis", "flashburn"),
    "shadow": ("poison", "shadowblight"),
}
SKIP_VARIANT = ("RNG", "mass")
DRG = "drg"
DEFAULT = "default"
DDRIVE = "ddrive"

ROOT_DIR = os.getenv("ROOT_DIR", os.path.realpath(os.path.join(__file__, "../..")))


SELF_TARGETS = ("MYSELF", "ALLY", "MYPARTY", "ALLY_HP_LOWEST", "MYSELF_CHECK_COLLISION", "HIT_OR_GUARDED_RECORD_MYSELF")
SELF = "self"
TEAM_TARGETS = ("ALLY", "MYPARTY", "MYPARTY_EXCEPT_MYSELF", "MYPARTY_EXCEPT_SAME_CHARID", "HIT_OR_GUARDED_RECORD_ALLY")
TEAM = "team"
ENEMY_TARGETS = ("HOSTILE", "HOSTILE_AND_DUNOBJ", "HIT_OR_GUARDED_RECORD")
ENEMY = "enemy"

GENERIC_TARGET = defaultdict(set)
for target in SELF_TARGETS:
    GENERIC_TARGET[target].add(SELF)
for target in TEAM_TARGETS:
    GENERIC_TARGET[target].add(TEAM)
for target in ENEMY_TARGETS:
    GENERIC_TARGET[target].add(ENEMY)

AFFLICTION_LIST = (
    "poison",
    "paralysis",
    "burn",
    "blind",
    "bog",
    "stun",
    "freeze",
    "sleep",
    "frostbite",
    "flashburn",
    "shadowblight",
    "stormlash",
    "scorchrend",
)

AFFRES_PROFILES = {
    None: {
        "poison": 0,
        "burn": 0,
        "paralysis": 0,
        "frostbite": 0,
        "flashburn": 0,
        "shadowblight": 0,
        "stormlash": 0,
        "scorchrend": 0,
        "blind": 99,
        "bog": 99,
        "freeze": 99,
        "stun": 99,
        "sleep": 99,
    },
    "immune": {
        "poison": 999,
        "burn": 999,
        "paralysis": 999,
        "frostbite": 999,
        "flashburn": 999,
        "shadowblight": 999,
        "stormlash": 999,
        "scorchrend": 999,
        "blind": 999,
        "bog": 999,
        "freeze": 999,
        "stun": 999,
        "sleep": 999,
    },
    ("flame", False): {  # Legend Volk
        "poison": 0,
        "burn": 0,
        "freeze": 100,
        "paralysis": 100,
        "blind": 99,
        "stun": 99,
        "bog": 99,
        "sleep": 99,
        "frostbite": 0,
        "flashburn": 0,
        "stormlash": 0,
        "shadowblight": 0,
        "scorchrend": 0,
    },
    ("flame", True): {  # Master Jaldabaoth (wind side)
        "poison": 100,
        "burn": 60,
        "freeze": 100,
        "paralysis": 100,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 100,
        "flashburn": 100,
        "stormlash": 100,
        "shadowblight": 100,
        "scorchrend": 0,
    },
    ("shadow", False): {  # Legend Kai Yan
        "poison": 0,
        "burn": 0,
        "freeze": 100,
        "paralysis": 100,
        "blind": 100,
        "stun": 99,
        "bog": 99,
        "sleep": 99,
        "frostbite": 0,
        "flashburn": 0,
        "stormlash": 0,
        "shadowblight": 0,
        "scorchrend": 0,
    },
    ("shadow", True): {  # Master Asura (light Side)
        "poison": 80,
        "burn": 100,
        "freeze": 100,
        "paralysis": 100,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 100,
        "flashburn": 100,
        "stormlash": 100,
        "shadowblight": 80,
        "scorchrend": 100,
    },
    ("wind", False): {  # Legend Ciella
        "poison": 85,
        "burn": 100,
        "freeze": 100,
        "paralysis": 100,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 100,
        "flashburn": 100,
        "stormlash": 20,
        "shadowblight": 100,
        "scorchrend": 100,
    },
    ("wind", True): {  # Master Iblis (water side)
        "poison": 0,
        "burn": 100,
        "freeze": 100,
        "paralysis": 100,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 100,
        "flashburn": 100,
        "stormlash": 0,
        "shadowblight": 100,
        "scorchrend": 100,
    },
    ("water", False): {  # Legend Ayaha & Otoha
        "poison": 100,
        "burn": 0,
        "freeze": 100,
        "paralysis": 100,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 0,
        "flashburn": 100,
        "stormlash": 100,
        "shadowblight": 100,
        "scorchrend": 100,
    },
    ("water", True): {  # Master Surtr (flame side)
        "poison": 85,
        "burn": 85,
        "freeze": 100,
        "paralysis": 85,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 0,
        "flashburn": 85,
        "stormlash": 85,
        "shadowblight": 0,
        "scorchrend": 85,
    },
    ("light", False): {  # Legend Tartarus
        "poison": 200,
        "burn": 200,
        "freeze": 200,
        "paralysis": 85,
        "blind": 200,
        "stun": 200,
        "bog": 200,
        "sleep": 200,
        "frostbite": 200,
        "flashburn": 20,
        "stormlash": 200,
        "shadowblight": 200,
        "scorchrend": 200,
    },
    ("light", True): {  # Master Lilith (shadow side)
        "poison": 100,
        "burn": 100,
        "freeze": 100,
        "paralysis": 30,
        "blind": 100,
        "stun": 100,
        "bog": 100,
        "sleep": 100,
        "frostbite": 100,
        "flashburn": 30,
        "stormlash": 100,
        "shadowblight": 100,
        "scorchrend": 100,
    },
}
OPS = {
    ">=": operator.ge,
    "<=": operator.le,
    "=": operator.eq,
    "<": operator.lt,
    ">": operator.gt,
}


def get_conf_json_path(fn):
    froot = os.path.join(ROOT_DIR, "conf")
    return os.path.join(froot, fn)


def save_json(fn, data, indent=None):
    fpath = get_conf_json_path(fn)
    with open(fpath, "w", encoding="utf8") as f:
        return json.dump(data, f, ensure_ascii=False, default=str, indent=indent)


def load_json(fn, fuzzy=False):
    fpath = get_conf_json_path(fn)
    if fuzzy:
        fpath_glob = glob.glob(fpath)
        if not fpath_glob:
            raise FileNotFoundError(fpath)
        fpath = fpath_glob[0]
    with open(fpath, "r", encoding="utf8") as f:
        return json.load(f, parse_float=float, parse_int=int)


wyrmprints = load_json("wyrmprints.json")
wyrmprints_meta = load_json("wyrmprints_meta.json")
# weapons = load_json('weapons.json')

baseconfs = {}
weapons = {}
for wep in WEAPON_TYPES:
    baseconfs[wep] = load_json(f"base/{wep}.json")
    weapons[wep] = load_json(f"wep/{wep}.json")


@functools.cache
def load_adv_json(adv, ele=None):
    if ele is not None:
        return load_json(f"adv/{ele}/{adv}.json")
    return load_json(f"adv/*/{adv}.json", fuzzy=True)


def list_adv_by_element(ele):
    for fpath in glob.glob(get_conf_json_path(f"adv/{ele}/*.json")):
        yield os.path.splitext(os.path.basename(fpath))[0]


def load_adv_by_element(ele):
    advs = {}
    for fpath in glob.glob(get_conf_json_path(f"adv/{ele}/*.json")):
        adv = os.path.splitext(os.path.basename(fpath))[0]
        advs[adv] = load_adv_json(ele=ele)
    return advs


@functools.cache
def load_drg_json(drg, ele=None):
    if ele is not None:
        return load_json(f"drg/{ele}/{drg}.json")
    return load_json(f"drg/*/{drg}.json", fuzzy=True)


def load_drg_by_element(ele):
    dragons = {}
    for fpath in glob.glob(get_conf_json_path(f"drg/{ele}/*.json")):
        drg = os.path.splitext(os.path.basename(fpath))[0]
        dragons[drg] = load_drg_json(drg, ele=ele)
    return dragons


def get_icon(adv):
    try:
        return load_adv_json(adv)["c"]["icon"]
    except (FileNotFoundError, KeyError):
        return ""


def get_fullname(adv):
    try:
        return load_adv_json(adv)["c"]["name"]
    except (FileNotFoundError, KeyError):
        return adv


def get_adv(name):
    conf = Conf(load_adv_json(name))

    wt = conf.c.wt
    base = baseconfs[wt]
    baseconf = Conf(base)
    if wt in AUTO_FSF:
        baseconf["x5"]["auto_fsf"] = True

    if bool(conf.c.spiral):
        baseconf.update(baseconf.lv2)
    del baseconf["lv2"]

    if wt == "gun" and len(conf.c.gun) == 1:
        # move gun[n] to base combo
        target = conf.c.gun[0]
        for xn, xconf in list(baseconf.find(r"^(x\d|fsf?)_gun\d$")):
            if int(xn[-1]) == target:
                baseconf[xn.split("_")[0]] = xconf
            del baseconf[xn]
        # ban fsf on gun2
        if conf.c.gun[0] == 2:
            baseconf.cannot_fsf = True

    conf.update(baseconf, rebase=True)

    return conf


def all_subclasses(cl):
    return set(cl.__subclasses__()).union([s for c in cl.__subclasses__() for s in all_subclasses(c)])


def subclass_dict(cl):
    return {sub_class.__name__: sub_class for sub_class in all_subclasses(cl)}


def float_ceil(value, percent):
    c_float_value = c_float(c_float(percent).value * value).value
    int_value = int(c_float_value)
    return int_value if int_value == c_float_value else int_value + 1
