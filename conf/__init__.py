import json
import os

from core import Conf

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

ROOT_DIR = os.getenv("ROOT_DIR", os.path.realpath(os.path.join(__file__, "../..")))


def get_conf_json_path(fn):
    froot = os.path.join(ROOT_DIR, "conf")
    return os.path.join(froot, fn)


def save_json(fn, data, indent=None):
    fpath = get_conf_json_path(fn)
    with open(fpath, "w", encoding="utf8") as f:
        return json.dump(data, f, ensure_ascii=False, default=str, indent=indent)


def load_json(fn):
    fpath = get_conf_json_path(fn)
    with open(fpath, "r", encoding="utf8") as f:
        return json.load(f, parse_float=float, parse_int=int)


exability = load_json("exability.json")
skillshare = load_json("skillshare.json")
wyrmprints = load_json("wyrmprints.json")
# weapons = load_json('weapons.json')

baseconfs = {}
weapons = {}
for wep in WEAPON_TYPES:
    baseconfs[wep] = load_json(f"base/{wep}.json")
    weapons[wep] = load_json(f"wep/{wep}.json")

dragons = {}
for ele in ELEMENTS:
    dragons[ele] = load_json(f"drg/{ele}.json")

alias = {}
for target, alst in load_json("alias.json").items():
    for a in alst:
        alias[a] = target

elecoabs = {}
for ele in ELEMENTS:
    elecoabs[ele] = {**exability["any"], **exability["generic"], **exability[ele]}

mono_elecoabs = {}
for ele in ELEMENTS:
    mono_elecoabs[ele] = {**exability["generic"], **exability[ele]}

advconfs = {}


def load_adv_json(adv):
    try:
        return advconfs[adv]
    except KeyError:
        aconf = load_json(f"adv/{adv}.json")
        advconfs[adv] = aconf
        return aconf


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


def get_adv_coability(adv):
    try:
        advcoabs = set()
        advconf = load_adv_json(adv)
        try:
            uniquecoab = elecoabs[advconf["c"]["ele"]][adv]
            advcoabs.add(adv)
            advcoabs.add(uniquecoab["category"])
        except KeyError:
            advcoabs.add(advconf["c"]["wt"].upper())
        return advcoabs
    except (FileNotFoundError, KeyError) as e:
        return None


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


def list_advs():
    for fn in sorted(os.listdir(os.path.join(ROOT_DIR, "conf", "adv"))):
        fn, ext = os.path.splitext(fn)
        if ext != ".json":
            continue
        yield fn
