import json
import os
import glob

from core import Conf
import functools

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


SELF_TARGETS = ("MYSELF", "ALLY", "MYPARTY", "ALLY_HP_LOWEST", "HIT_OR_GUARDED_RECORD_MYSELF")
TEAM_TARGETS = ("ALLY", "MYPARTY", "MYPARTY_EXCEPT_MYSELF", "MYPARTY_EXCEPT_SAME_CHARID")
ENEMY_TARGETS = ("HOSTILE", "HOSTILE_AND_DUNOBJ")


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
        fpath = glob.glob(fpath)[0]
    with open(fpath, "r", encoding="utf8") as f:
        return json.load(f, parse_float=float, parse_int=int)


wyrmprints = load_json("wyrmprints.json")
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
