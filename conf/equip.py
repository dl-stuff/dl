import json
import itertools
from enum import Enum
from pprint import pprint

from core.afflic import AFFLICT_LIST
from conf import (
    get_conf_json_path,
    ELE_AFFLICT,
    load_json,
    mono_elecoabs,
)


TDPS_WEIGHT = 15000
BUFFER_TDPS_THRESHOLD = 40000
BUFFER_TEAM_THRESHOLD = 1.6
BANNED_PRINTS = (
    # srry no full hp sd allowed
    "Witchs_Kitchen",
    "Berry_Lovable_Friends",
    "Happier_Times",
    # bugged in game
    "United_by_One_Vision",
    "Second_Anniversary",
    # corrosion
    "Her_Beloved_Crown",
    "Her_Beloved_Sword",
)
BANNED_SHARES = ("Durant", "Yue")
ABNORMAL_COND = (
    "sim_buffbot",
    "dragonbattle",
    "berserk",
    "classbane",
    "hp",
    "dumb",
    "fleet",
)
HAS_7SLOT = ("light",)
DEFAULT_MONO_COABS = {
    "flame": ("Blade", "Wand", "Dagger", "Bow"),
    "water": ("Blade", "Wand", "Dagger", "Bow"),
    "wind": ("Blade", "Mona", "Dragonyule_Xainfried", "Dagger"),
    "light": ("Blade", "Peony", "Wand", "Dagger"),
    "shadow": ("Blade", "Wand", "Dagger", "Bow"),
}
BUILD_CONF_KEYS = ("slots.a", "slots.d", "slots.w", "acl", "coabs", "share")
BUILD_META_KEYS = ("dps", "team")


class ValueEnum(Enum):
    def __str__(self):
        return str(self.value)


class AfflictionCondition(ValueEnum):
    SELF = "SELF"
    ALWAYS = "ALWAYS"
    IMMUNE = "IMMUNE"

    @classmethod
    def get_condition(cls, adv):
        affres = adv.afflics.get_resist()
        if all((value >= 300 for value in affres.values())):
            return cls.IMMUNE
        if not adv.sim_afflict:
            return cls.SELF
        eleaff = ELE_AFFLICT[adv.slots.c.ele]
        if adv.sim_afflict == {eleaff} and getattr(adv.afflics, eleaff).get_override == 1:
            return cls.ALWAYS
        raise ValueError("Invalid affliction condition")

    def get_conf(self):
        if self == AfflictionCondition.IMMUNE:
            return {"afflict_res": {aff: 999 for aff in AFFLICT_LIST}}
        if self == AfflictionCondition.ALWAYS:
            return {"sim_afflict": {"onele": True}}
        return {}


class NihilismCondition(ValueEnum):
    NORMAL = "NORMAL"
    NIHILISM = "NIHILISM"

    @classmethod
    def get_condition(cls, adv):
        if adv.nihilism:
            return cls.NIHILISM
        return cls.NORMAL

    def get_conf(self):
        if self == NihilismCondition.NIHILISM:
            return {"nihilism": True}
        return {}


def all_monoele_coabs(adv):
    return all((coab in mono_elecoabs[adv.slots.c.ele] for coab in adv.slots.c.coab_list))


class MonoCondition(ValueEnum):
    ANY = "ANY"
    MONO = "MONO"

    @classmethod
    def get_condition(cls, adv):
        if all_monoele_coabs(adv):
            return cls.MONO
        return cls.ANY

    def get_conf(self):
        return {}


class ConditionTuple(tuple):
    SEPARATOR = "-"

    def __str__(self):
        return ConditionTuple.SEPARATOR.join(map(str, self))

    @property
    def aff(self):
        return self[0]

    @property
    def nihil(self):
        return self[1]

    @property
    def mono(self):
        return self[2]

    def reduced(self):
        aff, nihil, mono = self
        return (
            ConditionTuple((AfflictionCondition.SELF, nihil, mono)),
            ConditionTuple((aff, NihilismCondition.NORMAL, mono)),
            ConditionTuple((AfflictionCondition.SELF, NihilismCondition.NORMAL, mono)),
        )

    def mono_to_any(self):
        aff, nihil, _ = self
        return ConditionTuple((aff, nihil, MonoCondition.ANY))

    def get_conf(self):
        conf = {}
        for value in self:
            conf.update(value.get_conf())
        return conf


def dps_weight(entry):
    return entry["dps"] + entry["team"] * TDPS_WEIGHT


class OpimizationMode(ValueEnum):
    PERSONAL = "PERSONAL"
    TEAMBUFF = "TEAMBUFF"


def equivalent(a, b):
    try:
        return set(a) == set(b)
    except (ValueError, TypeError):
        return a == b


def same_build(entry_a, entry_b):
    return all((equivalent(entry_a.get(k), entry_b.get(k)) for k in BUILD_CONF_KEYS))


def same_coab_build(entry_a, entry_b):
    return set(entry_a["coabs"]) == set(entry_b["coabs"])


def dps_only(entry_a):
    return set(entry_a.keys()) == {"dps", "team"}


def same_build_different_dps(entry_a, entry_b):
    return same_build(entry_a, entry_b) and any((entry_a.get(k) != entry_b.get(k) for k in BUILD_META_KEYS))


def compare_build_personal(entry_a, entry_b):
    return dps_weight(entry_a) >= dps_weight(entry_b)


def compare_build_teambuff(entry_a, entry_b):
    return entry_a["team"] > entry_b["team"] or (round(entry_a["team"], 5) == round(entry_b["team"], 5) and entry_a["dps"] > entry_b["dps"])


OPT_COMPARE = {
    OpimizationMode.PERSONAL: compare_build_personal,
    OpimizationMode.TEAMBUFF: compare_build_teambuff,
}
OPT_KICK = {
    OpimizationMode.PERSONAL: OpimizationMode.TEAMBUFF,
    OpimizationMode.TEAMBUFF: OpimizationMode.PERSONAL,
}


def build_from_sim(adv, real_d):
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    build = {"dps": ndps, "team": nteam}
    build["slots.a"] = adv.slots.a.qual_lst
    build["slots.d"] = adv.slots.d.qual
    if adv.slots.w.qual != adv.slots.DEFAULT_WEAPON:
        build["slots.w"] = adv.slots.w.qual
    acl_list = adv.conf.acl
    if not isinstance(acl_list, list):
        acl_list = [line.strip() for line in acl_list.split("\n") if line.strip()]
    build["acl"] = acl_list
    build["coabs"] = adv.slots.c.coab_list
    build["share"] = adv.skillshare_list
    return build


def coab_only_build(build):
    return {"dps": build["dps"], "team": build["team"], "coabs": build["coabs"]}


def dps_only_build(build):
    return {"dps": build["dps"], "team": build["team"]}


def validate_sim(adv):
    adv.duration = int(adv.duration)
    wp_qual_lst = adv.slots.a.qual_lst
    return (
        adv.duration == 180
        and all([not k in adv.conf for k in ABNORMAL_COND])
        and all([not wp in BANNED_PRINTS for wp in wp_qual_lst])
        and all([not ss in BANNED_SHARES for ss in adv.skillshare_list])
        and len(adv.slots.c.coab_list) == 3
        and ((len(wp_qual_lst) > 5 and adv.slots.c.ele in HAS_7SLOT and adv.slots.w.qual == "Agito") or len(wp_qual_lst) == 5)
    )


class EquipEntry(dict):
    def __init__(self, conditions):
        converted = {
            OpimizationMode.PERSONAL: None,
            OpimizationMode.TEAMBUFF: None,
            "META": {"tdps": None, "pref": OpimizationMode.PERSONAL},
        }
        self._conditions = conditions
        super().__init__(converted)
        self._downgrade = None
        self._default = None

    def from_dict(self, builds):
        for k, v in builds.items():
            if k == "META":
                v["pref"] = OpimizationMode(v["pref"])
                self[k] = v
            else:
                self[OpimizationMode(k)] = v

    def builds(self):
        for opt in OpimizationMode:
            yield opt, self.get_build(opt)

    @property
    def tdps(self):
        return self["META"]["tdps"]

    @tdps.setter
    def tdps(self, tdps):
        self["META"]["tdps"] = tdps

    @property
    def pref(self):
        return self["META"]["pref"]

    @pref.setter
    def pref(self, pref):
        self["META"]["pref"] = pref

    def get_build(self, opt):
        build = self[opt]
        if not build:
            build = self[OPT_KICK[opt]]
        if not build and self._downgrade:
            build = self._downgrade.get_build(opt)
        if self._default:
            if not build:
                build = self._default.get_build(opt)
            elif dps_only(build):
                build.update(self._default[opt])
        return build

    @property
    def preferred(self):
        return self.get_build(self.pref)

    @property
    def empty(self):
        return not any((self[opt] for opt in OpimizationMode))

    def update_meta(self):
        personal_build = self.get_build(OpimizationMode.PERSONAL)
        teambuff_build = self.get_build(OpimizationMode.TEAMBUFF)
        if not teambuff_build:
            self.tdps = None
            self.pref = OpimizationMode.PERSONAL
            return
        if not personal_build:
            self.tdps = None
            self.pref = OpimizationMode.TEAMBUFF
            return

        if personal_build["team"] != teambuff_build["team"]:
            self.tdps = (personal_build["dps"] - teambuff_build["dps"]) / (teambuff_build["team"] - personal_build["team"])
        else:
            self.tdps = None

        if teambuff_build["team"] > BUFFER_TEAM_THRESHOLD or (self.tdps is not None and self.tdps < BUFFER_TDPS_THRESHOLD):
            self.pref = OpimizationMode.TEAMBUFF
        else:
            self.pref = OpimizationMode.PERSONAL

    def set_build(self, opt, build):
        if self._conditions.mono == MonoCondition.MONO:
            self[opt] = coab_only_build(build)
        else:
            self[opt] = build

    def accept_new_build(self, new_build):
        changed = False
        kicked = {}
        for opt, existing_build in self.builds():
            if not existing_build or same_build_different_dps(new_build, existing_build) or OPT_COMPARE[opt](new_build, existing_build):
                self.set_build(opt, new_build)
                if existing_build:
                    kicked[OPT_KICK[opt]] = existing_build
                changed = True
        for opt, kicked_build in kicked.items():
            if not self[opt] or same_build_different_dps(kicked_build, self[opt]) or OPT_COMPARE[opt](kicked_build, self[opt]):
                self.set_build(opt, kicked_build)
                changed = True
        if self._downgrade:
            changed = self._downgrade.accept_new_build(new_build) or changed
            for opt, reference_build in self._downgrade.builds():
                print(f"CHECK {self._conditions}.{opt}")
                pprint(self[opt])
                print(f"AGAINST {self._downgrade._conditions}.{opt}")
                pprint(reference_build)
                if self[opt]:
                    if same_coab_build(self[opt], reference_build) or OPT_COMPARE[opt](reference_build, self[opt]):
                        self[opt] = None
                        changed = True
        if self._default:
            for opt, reference_build in self._default.builds():
                if self[opt] and not dps_only(self[opt]) and same_build(self[opt], reference_build):
                    self[opt] = dps_only_build(self[opt])
                    changed = True
        if changed:
            self.update_meta()
        return changed


def encodable(data):
    if isinstance(data, EquipEntry) and data.empty:
        return None
    if isinstance(data, dict):
        output = {}
        for k, v in data.items():
            encodable_v = encodable(v)
            if encodable_v is not None:
                output[str(k)] = encodable_v
        return output
    return data


class EquipManager(dict):
    EQUIP_DIR = "equip.new"
    ALL_COND_ENUMS = (AfflictionCondition, NihilismCondition, MonoCondition)

    def __init__(self, advname, debug=False):
        self._advname = advname
        self._equip_file = get_conf_json_path(f"{EquipManager.EQUIP_DIR}/{advname}.json")
        self.debug = debug
        for conditions in map(ConditionTuple, itertools.product(*EquipManager.ALL_COND_ENUMS)):
            self[conditions] = EquipEntry(conditions)
        try:
            for key, value in self.load_equip_json():
                aff, nihil, mono = key.split(ConditionTuple.SEPARATOR)
                conditions = ConditionTuple((AfflictionCondition(aff), NihilismCondition(nihil), MonoCondition(mono)))
                self[conditions].from_dict(value)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        self._default_conditions = ConditionTuple((AfflictionCondition.SELF, NihilismCondition.NORMAL, MonoCondition.ANY))
        for key, value in self.items():
            if key.mono == MonoCondition.MONO:
                value._downgrade = self.get(key.mono_to_any())
            if key != self._default_conditions:
                value._default = self.get(self._default_conditions)

    def get_preferred_entry(self, conditions):
        if conditions is None:
            return self[self._default_conditions].preferred, self._default_conditions
        conditions = ConditionTuple(conditions)
        preferred = self[conditions].preferred
        if preferred:
            return preferred, conditions

        for r_cond in conditions.reduced():
            preferred = self[r_cond].preferred
            if preferred:
                return preferred, r_cond

        return None, conditions

    def load_equip_json(self):
        with open(self._equip_file, "r", encoding="utf8") as f:
            return json.load(f, parse_float=float, parse_int=int).items()

    def save_equip_json(self):
        with open(self._equip_file, "w", encoding="utf8") as f:
            return json.dump(encodable(self), f, ensure_ascii=False, default=str, indent=2)

    def accept_new_entry(self, adv, real_d):
        if not validate_sim(adv):
            return
        try:
            conditions = ConditionTuple((cond_enum.get_condition(adv) for cond_enum in EquipManager.ALL_COND_ENUMS))
        except ValueError:
            return
        new_build = build_from_sim(adv, real_d)
        changed = self[conditions].accept_new_build(new_build)
        if changed:
            self.save_equip_json()


def _test_equip(advname, confs=None):
    import core.simulate

    adv_module, advname = core.simulate.load_adv_module(advname)
    equip_manager = EquipManager(advname)
    equip_manager.save_equip_json()
    for conf in confs:
        run_res = core.simulate.test(advname, adv_module, conf, 180)
        adv = run_res[0][0]
        real_d = run_res[0][1]
        equip_manager.accept_new_entry(adv, real_d)
    return equip_manager

    # "base": BaseEntry,
    # "buffer": BufferEntry,
    # "affliction": AfflictionEntry,
    # "noaffliction": NoAfflictionEntry,
    # # 'affbuff' ?
    # "mono_base": MonoBaseEntry,
    # "mono_buffer": MonoBufferEntry,
    # "mono_affliction": MonoAfflictionEntry,
    # "mono_noaffliction": MonoNoAfflictionEntry,


OLD_KEY_TO_COND = {
    "base": ConditionTuple((AfflictionCondition.SELF, NihilismCondition.NORMAL, MonoCondition.ANY)),
    "buffer": ConditionTuple((AfflictionCondition.SELF, NihilismCondition.NORMAL, MonoCondition.ANY)),
    "affliction": ConditionTuple((AfflictionCondition.ALWAYS, NihilismCondition.NORMAL, MonoCondition.ANY)),
    "noaffliction": ConditionTuple((AfflictionCondition.IMMUNE, NihilismCondition.NORMAL, MonoCondition.ANY)),
    "mono_base": ConditionTuple((AfflictionCondition.SELF, NihilismCondition.NORMAL, MonoCondition.MONO)),
    "mono_buffer": ConditionTuple((AfflictionCondition.SELF, NihilismCondition.NORMAL, MonoCondition.MONO)),
    "mono_affliction": ConditionTuple((AfflictionCondition.ALWAYS, NihilismCondition.NORMAL, MonoCondition.MONO)),
    "mono_noaffliction": ConditionTuple((AfflictionCondition.IMMUNE, NihilismCondition.NORMAL, MonoCondition.MONO)),
}


def convert_from_existing(advname):
    old_equip = load_json(f"equip/{advname}.json")
    old_180s = old_equip["180"]
    confs = []
    for key, conf in old_180s.items():
        if isinstance(conf, str):
            continue
        conf = dict(conf)
        condition = OLD_KEY_TO_COND[key]
        if condition.mono == MonoCondition.MONO:
            try:
                baseconf = dict(old_180s[key.split("_")[-1]])
                baseconf.update(conf)
                conf = baseconf
            except KeyError:
                pass
        pprint(f"CONF {condition}: {condition.get_conf()}")
        conf.update(condition.get_conf())
        confs.append(conf)
    _test_equip(advname, confs)


if __name__ == "__main__":
    convert_from_existing("Xania")