import itertools
from enum import Enum

from conf import (
    load_json,
    save_json,
    ELE_AFFLICT,
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
        return self.value


class AfflictionCondition(ValueEnum):
    SELF = 0
    ALWAYS = 1
    IMMUNE = -1

    @classmethod
    def get_condition(cls, adv):
        affres = adv.afflics.get_resist()
        if all((value >= 300 for value in affres.values())):
            return cls.IMMUNE
        if not adv.sim_afflict:
            return cls.SELF
        eleaff = ELE_AFFLICT[adv.slots.c.ele]
        if adv.sim_afflict == {eleaff} and adv.conf_init.sim_afflict[eleaff] == 1:
            return cls.ALWAYS


class NihilismCondition(ValueEnum):
    NORMAL = 0
    NIHILISM = 1

    @classmethod
    def get_condition(cls, adv):
        if adv.nihilism:
            return cls.NIHILISM
        return cls.NORMAL


def all_monoele_coabs(adv):
    return all((coab in mono_elecoabs[adv.slots.c.ele] for coab in adv.slots.c.coab_list))


class MonoCondition(ValueEnum):
    ANY = 0
    MONO = 1

    @classmethod
    def get_condition(cls, adv):
        if all_monoele_coabs(adv):
            return cls.MONO
        return cls.ANY


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
            ConditionTuple(AfflictionCondition.SELF, nihil, mono),
            ConditionTuple(aff, NihilismCondition.NORMAL, mono),
            ConditionTuple(AfflictionCondition.SELF, NihilismCondition.NORMAL, mono),
        )


def dps_weight(entry):
    return entry["dps"] + entry["team"] * TDPS_WEIGHT


class OpimizationMode(ValueEnum):
    PERSONAL = 0
    TEAMBUFF = 1


def same_build(entry_a, entry_b):
    return all((equivalent(entry_a.get(k), entry_b.get(k)) for k in BUILD_CONF_KEYS))


def same_build_different_dps(entry_a, entry_b):
    return entry_a.same_build(entry_b) and any((entry_a.get(k) != entry_b.get(k) for k in BUILD_META_KEYS))


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


def build_from_sim(adv, real_d, coab_only=False):
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    build = {"dps": ndps, "team": nteam}
    if coab_only:
        build["coabs"] = adv.slots.c.coab_list
        return build
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


def equivalent(a, b):
    try:
        return set(a) == set(b)
    except (ValueError, TypeError):
        return a == b


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

    def from_dict(self, builds):
        for k, v in builds.items():
            if k == "META":
                self[k] = v
            else:
                self[OpimizationMode(k)] = v

    @property.setter
    def downgrade(self, downgrade):
        self._downgrade = downgrade

    def builds(self):
        for opt in OpimizationMode:
            yield opt, self[opt]

    @property.setter
    def tdps(self, tdps):
        self["META"]["tdps"] = tdps

    @property.getter
    def tdps(self):
        return self["META"]["tdps"]

    @property.setter
    def pref(self, pref):
        self["META"]["pref"] = pref

    @property.getter
    def pref(self):
        return self["META"]["pref"]

    def get_build(self, opt):
        personal_build = self[opt]
        if not personal_build and self._downgrade:
            personal_build = self._downgrade[opt]
        return personal_build

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

        if teambuff_build["team"] > BUFFER_TEAM_THRESHOLD or self.tdps < BUFFER_TDPS_THRESHOLD:
            self.pref = OpimizationMode.TEAMBUFF
        else:
            self.pref = OpimizationMode.PERSONAL

    def accept_new_build(self, new_build):
        changed = False
        kicked = {}
        for opt, existing_build in self.builds():
            if not existing_build or same_build_different_dps(new_build, existing_build) or OPT_COMPARE[opt](new_build, existing_build):
                self[opt] = new_build
                kicked[OPT_KICK[opt]] = existing_build
                changed = True
        for opt, kicked_build in self.builds():
            if not self[opt] or same_build_different_dps(new_build, existing_build) or OPT_COMPARE[opt](kicked_build, self[opt]):
                self[opt] = kicked_build
                changed = True
        if self._downgrade:
            changed = self._downgrade.accept_new_build(new_build) or changed
            for opt, reference_build in self._downgrade.builds():
                if same_build(self[opt], reference_build):
                    self[opt] = None
                    changed = True
        if changed:
            self.update_meta()
        return changed


class EquipManager(dict):
    ALL_COND_ENUMS = (AfflictionCondition, NihilismCondition, MonoCondition)

    def __init__(self, advname, debug=False):
        self._advname = advname
        self._equip_file = f"equip/{advname}.json"
        self.debug = debug
        for conditions in map(ConditionTuple, itertools.product(*EquipManager.ALL_COND_ENUMS)):
            self[conditions] = EquipEntry(conditions)
        try:
            for key, value in load_json(self._equip_file):
                aff, nihil, mono = map(int, key.split(ConditionTuple.SEPARATOR))
                conditions = ConditionTuple(AfflictionCondition(aff), NihilismCondition(nihil), MonoCondition(mono))
                self[conditions].from_dict(value)
        except FileNotFoundError:
            pass
        for key, value in self.items():
            if key[2] == MonoCondition.MONO:
                value.downgrade = self.get(key[0], key[1], MonoCondition.ANY)

    def get_preferred_entry(self, conditions):
        preferred = self[conditions].preferred
        if preferred:
            return preferred

        for r_cond in conditions.reduced():
            preferred = self[r_cond].preferred
            if preferred:
                return preferred

    def write_equip_json(self):
        save_json(self._equip_file)

    def accept_new_entry(self, adv, real_d):
        if not validate_sim(adv):
            return
        conditions = tuple((cond_enum.get_condition(adv) for cond_enum in EquipManager.ALL_COND_ENUMS))
        new_build = build_from_sim(adv, real_d, coab_only=(conditions.mono == MonoCondition.MONO))
        changed = self[conditions].accept_new_build(new_build)