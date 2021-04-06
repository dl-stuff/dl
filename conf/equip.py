import json
import itertools
import os
import shutil
from enum import Enum
from pprint import pprint

from core.afflic import AFFLICT_LIST
from conf import (
    SKIP_VARIANT,
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
DEBUG = True


class ValueEnum(Enum):
    def __str__(self):
        return str(self.value)


class AfflictionCondition(ValueEnum):
    SELF = "SELF"
    ALWAYS = "ALWAYS"
    IMMUNE = "IMMUNE"

    @classmethod
    def get_condition(cls, adv):
        if not adv.uses_affliction() or all((value >= 300 for value in adv.afflics.get_resist().values())):
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


class SituationCondition(ValueEnum):
    NORMAL = "NORMAL"
    NIHILISM = "NIHILISM"

    @classmethod
    def get_condition(cls, adv):
        if adv.nihilism:
            return cls.NIHILISM
        return cls.NORMAL

    def get_conf(self):
        if self == SituationCondition.NIHILISM:
            return {"nihilism": True}
        return {}


def all_monoele_coabs(ele, coab_list):
    return all((coab in mono_elecoabs[ele] for coab in coab_list))


class MonoCondition(ValueEnum):
    ANY = "ANY"
    MONO = "MONO"

    @classmethod
    def get_condition(cls, adv):
        if all_monoele_coabs(adv.slots.c.ele, adv.slots.c.coab_list):
            return cls.MONO
        return cls.ANY

    def get_conf(self):
        return {}


class ConditionTuple(tuple):
    SEPARATOR = "-"

    def __str__(self):
        return ConditionTuple.SEPARATOR.join(map(str, self))

    @staticmethod
    def from_str(key):
        aff, sit, mono = key.split(ConditionTuple.SEPARATOR)
        return ConditionTuple((AfflictionCondition(aff), SituationCondition(sit), MonoCondition(mono)))

    @property
    def aff(self):
        return self[0]

    @property
    def sit(self):
        return self[1]

    @property
    def mono(self):
        return self[2]

    def reduced(self):
        aff, sit, mono = self
        return (
            ConditionTuple((AfflictionCondition.SELF, sit, mono)),
            ConditionTuple((aff, SituationCondition.NORMAL, mono)),
            ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, mono)),
        )

    def aff_to_self(self):
        _, sit, mono = self
        return ConditionTuple((AfflictionCondition.SELF, sit, mono))

    def mono_to_any(self):
        aff, sit, _ = self
        return ConditionTuple((aff, sit, MonoCondition.ANY))

    def get_conf(self):
        conf = {}
        for value in self:
            conf.update(value.get_conf())
        return conf


DEFAULT_CONDITONS = ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, MonoCondition.ANY))


def dps_weight(entry):
    return entry["dps"] + entry["team"] * TDPS_WEIGHT


class OpimizationMode(ValueEnum):
    PERSONAL = "PERSONAL"
    TEAMBUFF = "TEAMBUFF"


def build_equip_condition(equip):
    if equip is None:
        return None
    aff = equip["aff"] or "SELF"
    sit = equip["sit"] or "NORMAL"
    mono = equip["mono"] or "ANY"
    try:
        opt = OpimizationMode(equip["opt"])
    except ValueError:
        opt = None
    return ConditionTuple((AfflictionCondition(aff), SituationCondition(sit), MonoCondition(mono))), opt


def equivalent(entry_a, entry_b, key):
    a = entry_a.get(key)
    b = entry_b.get(key)
    if key == "acl":
        return a == b
    try:
        return set(a) == set(b)
    except (ValueError, TypeError):
        return a == b


def same_build(entry_a, entry_b):
    return all((equivalent(entry_a, entry_b, key) for key in BUILD_CONF_KEYS))


def same_build_different_dps(entry_a, entry_b):
    return same_build(entry_a, entry_b) and any((entry_a.get(k) != entry_b.get(k) for k in BUILD_META_KEYS))


def compare_build_personal(entry_a, entry_b):
    return dps_weight(entry_a) >= dps_weight(entry_b)


def compare_build_teambuff(entry_a, entry_b):
    return (
        entry_a["team"] > 0
        and entry_a["team"] > entry_b["team"]
        or (round(entry_a["team"], 5) == round(entry_b["team"], 5) and entry_a["dps"] >= entry_b["dps"])
    )


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
    if adv.slots.w.series != adv.slots.DEFAULT_WEAPON:
        build["slots.w"] = adv.slots.w.series
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


def difference_of_builds(entry_a, entry_b):
    build_diff = {}
    for key in BUILD_CONF_KEYS:
        b_val = entry_b.get(key)
        if b_val and not equivalent(entry_a, entry_b, key):
            build_diff[key] = b_val
    return build_diff


def validate_sim(adv):
    adv.duration = int(adv.duration)
    if not adv.duration == 180:
        return False, "Duration not 180s"
    if not all([not k in adv.conf for k in ABNORMAL_COND]):
        return False, "Has an abnormal condition"
    wp_qual_lst = adv.slots.a.qual_lst
    if not all([not wp in BANNED_PRINTS for wp in wp_qual_lst]):
        return False, "Using a banned print"
    if not len(adv.slots.c.coab_list) == 3:
        return False, "Less than 3 coabilities"
    if adv.slots.c.ele in HAS_7SLOT and adv.slots.w.series == "agito":
        if not len(wp_qual_lst) == 7:
            return False, "Less than 7 wyrmprints"
    elif not len(wp_qual_lst) == 5:
        return False, "Less than 5 wyrmprints"
    return True, None


class EquipEntry(dict):
    def __init__(self, conditions):
        super().__init__({})
        self.reset()
        self._conditions = conditions
        self._mono_to_any = None
        self._aff_to_self = None
        self._default = None
        self._pref_override = None

    def reset(self):
        self[OpimizationMode.TEAMBUFF] = None
        self[OpimizationMode.PERSONAL] = None
        self["META"] = {
            "tdps": None,
            "pref": OpimizationMode.PERSONAL,
            "partial": {OpimizationMode.PERSONAL: None, OpimizationMode.TEAMBUFF: None},
        }

    def from_dict(self, builds):
        self.reset()
        for k, v in builds.items():
            if k == "META":
                v["pref"] = OpimizationMode(v["pref"])
                for opt, based_on in v.get("partial", {}).items():
                    v["partial"][opt] = ConditionTuple.from_str(based_on)
                self[k].update(v)
            else:
                self[OpimizationMode(k)] = v

    def builds(self):
        for opt in OpimizationMode:
            build = self.get_build(opt)
            yield opt, self.get_build(opt)

    @property
    def tdps(self):
        return self["META"]["tdps"]

    @tdps.setter
    def tdps(self, tdps):
        self["META"]["tdps"] = tdps

    @property
    def pref(self):
        return self._pref_override or self["META"]["pref"]

    @pref.setter
    def pref(self, pref):
        self["META"]["pref"] = pref

    def get_partial_base(self, opt):
        based_on = self["META"]["partial"][opt]
        if self._mono_to_any and based_on == self._mono_to_any._conditions:
            base_build = self._mono_to_any.get_build(opt)
            if base_build:
                return base_build, based_on
        if self._default and based_on == self._default._conditions:
            base_build = self._default.get_build(opt)
            if base_build:
                return base_build, based_on
        return None, None

    def get_build(self, opt, with_conditions=False):
        original_opt = opt
        while True:
            build = self[opt]
            if build:
                base_build, based_on = self.get_partial_base(opt)
                if base_build:
                    if with_conditions:
                        conditions = based_on if set(build.keys()) == BUILD_META_KEYS else self._conditions
                        return {**base_build, **build}, conditions
                    else:
                        return {**base_build, **build}
            else:
                if self._mono_to_any:
                    return self._mono_to_any.get_build(opt, with_conditions=with_conditions)
                if self._default:
                    return self._default.get_build(opt, with_conditions=with_conditions)
            if build or original_opt != opt:
                break
            opt = OPT_KICK[opt]
        return build, self._conditions

    @property
    def preferred(self):
        return self.get_build(self.pref, with_conditions=True)

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

        if personal_build["team"] < teambuff_build["team"]:
            self.tdps = (personal_build["dps"] - teambuff_build["dps"]) / (teambuff_build["team"] - personal_build["team"])
        else:
            self.tdps = None
            if same_build(personal_build, teambuff_build) and self._default is not None:
                self[OpimizationMode.TEAMBUFF] = None

        if teambuff_build["team"] > BUFFER_TEAM_THRESHOLD or (self.tdps is not None and self.tdps < BUFFER_TDPS_THRESHOLD):
            self.pref = OpimizationMode.TEAMBUFF
        else:
            self.pref = OpimizationMode.PERSONAL

    def set_build(self, opt, build):
        if DEBUG:
            print(f"ACCEPTED {self._conditions}.{opt}", flush=True)
        self[opt] = {**build}
        self["META"]["partial"][opt] = None

    def set_build_diff(self, opt, build_diff, based_on):
        if DEBUG:
            print(f"DIFF ONLY {self._conditions}.{opt}, {build_diff}", flush=True)
        self[opt] = {"dps": self[opt]["dps"], "team": self[opt]["dps"], **build_diff}
        self["META"]["partial"][opt] = based_on

    def delete_build(self, opt):
        if DEBUG:
            print(f"DELETED {self._conditions}.{opt}", flush=True)
        self[opt] = None
        self["META"]["partial"][opt] = None

    def accept_new_build(self, new_build, adv):
        if DEBUG:
            print("-" * 100)
            print(f"CHECKING {self._conditions}:")
            pprint(new_build)

        # in the case where we have aff -> self downgrading and this sim did not use afflictions, send build off to that
        if self._aff_to_self and not bool(adv.uses_affliction()):
            if DEBUG:
                print(f"PASSED from {self._conditions} to {self._aff_to_self._conditions} (_aff_to_self)")
            changed, accepted = self._aff_to_self.accept_new_build(new_build, adv)
            if accepted:
                return changed, accepted

        changed = False
        accepted = False
        kicked = {}
        # check against current builds
        for opt, existing_build in self.builds():
            if not existing_build or same_build_different_dps(new_build, existing_build) or OPT_COMPARE[opt](new_build, existing_build):
                self.set_build(opt, new_build)
                if existing_build and OPT_COMPARE[OPT_KICK[opt]](existing_build, new_build):
                    kicked[OPT_KICK[opt]] = existing_build
                changed = True
                accepted = True

        # check kicked build against the other opt mode
        for opt, kicked_build in kicked.items():
            if not self[opt] or same_build_different_dps(kicked_build, self[opt]) or OPT_COMPARE[opt](kicked_build, self[opt]):
                if DEBUG:
                    print("KICK")
                self.set_build(opt, kicked_build)
                changed = True

        # check mono build against the any build
        if self._mono_to_any:
            if DEBUG:
                print(f"PASSED from {self._conditions} to {self._mono_to_any._conditions} (_mono_to_any)")
            changed = self._mono_to_any.accept_new_build(new_build, adv)[0] or changed
            for opt, reference_build in self._mono_to_any.builds():
                if not self[opt]:
                    continue
                # check if any build is also a mono build, and is equal/better than this build
                if all_monoele_coabs(adv.slots.c.ele, reference_build["coabs"]) and OPT_COMPARE[opt](reference_build, self[opt]):
                    self.delete_build(opt)
                    changed = True
                    continue
                # check if the builds are different, and store only the parts that are not the same
                build_diff = difference_of_builds(reference_build, self[opt])
                if not build_diff:
                    self.delete_build(opt)
                    changed = True
                    continue
                self.set_build_diff(opt, build_diff, self._mono_to_any._conditions)

        # check build against the default build
        if self._default:
            for opt, reference_build in self._default.builds():
                if self[opt]:
                    # check if the builds are different, and store only the parts that are not the same
                    build_diff = difference_of_builds(reference_build, self[opt])
                    self.set_build_diff(opt, build_diff, self._default._conditions)

        if changed:
            self.update_meta()
        print("-" * 100)
        return changed, accepted


def encodable(data, key=None):
    if isinstance(data, EquipEntry) and data.empty:
        return None
    if isinstance(data, dict):
        output = {}
        for k, v in data.items():
            encodable_v = encodable(v, key=k)
            if encodable_v is not None:
                output[str(k)] = encodable_v
        if key == "partial":
            if not output:
                return None
            for k, v in output.items():
                output[k] = str(v)
        return output
    return data


class EquipManager(dict):
    EQUIP_DIR = "equip.new"
    ALL_COND_ENUMS = (AfflictionCondition, SituationCondition, MonoCondition)

    def __init__(self, advname, variant=None):
        self._advname = advname
        self._variant = variant
        if variant and variant not in SKIP_VARIANT:
            self._equip_file = get_conf_json_path(f"{EquipManager.EQUIP_DIR}/{advname}.{variant}.json")
            if not os.path.exists(self._equip_file):
                basefile = get_conf_json_path(f"{EquipManager.EQUIP_DIR}/{advname}.json")
                try:
                    shutil.copyfile(basefile, self._equip_file)
                except FileNotFoundError:
                    pass
        else:
            self._equip_file = get_conf_json_path(f"{EquipManager.EQUIP_DIR}/{advname}.json")
        for conditions in map(ConditionTuple, itertools.product(*EquipManager.ALL_COND_ENUMS)):
            self[conditions] = EquipEntry(conditions)
        try:
            for key, value in self.load_equip_json():
                conditions = ConditionTuple.from_str(key)
                self[conditions].from_dict(value)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

        for key, value in self.items():
            if key == DEFAULT_CONDITONS:
                continue
            if key.aff != AfflictionCondition.SELF:
                value._aff_to_self = self.get(key.aff_to_self())
            if key.mono == MonoCondition.MONO:
                value._mono_to_any = self.get(key.mono_to_any())
            value._default = self.get(DEFAULT_CONDITONS)

    def get_preferred_entry(self, conditions):
        if conditions is None:
            return self[DEFAULT_CONDITONS].preferred
        if not isinstance(conditions, ConditionTuple):
            conditions = ConditionTuple(conditions)

        preferred, p_cond = self[conditions].preferred
        if preferred:
            return preferred, p_cond

        for r_cond in conditions.reduced():
            preferred, r_cond = self[r_cond].preferred
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
        valid, failure = validate_sim(adv)
        if not valid:
            if DEBUG:
                print(f"INVALID SIM: {failure!r}")
            return
        try:
            conditions = ConditionTuple((cond_enum.get_condition(adv) for cond_enum in EquipManager.ALL_COND_ENUMS))
        except ValueError:
            return
        new_build = build_from_sim(adv, real_d)
        changed = self[conditions].accept_new_build(new_build, adv)
        if changed:
            self.save_equip_json()

    def repair_entries(self, advmodule):
        import core.simulate

        for conditions, entry in self.items():
            if entry.empty:
                continue
            for opt in OpimizationMode:
                if entry[opt] is None:
                    continue
                entry._pref_override = opt
                with open(os.devnull, "w") as output:
                    run_res = core.simulate.test(
                        self._advname,
                        advmodule,
                        duration=180,
                        verbose=0,
                        output=output,
                        equip_conditions=conditions,
                    )
                adv = run_res[0][0]
                real_d = run_res[0][1]
                entry[opt] = build_from_sim(adv, real_d)
            entry.update_meta()
            self.save_equip_json()

    def set_pref_override(self, pref_override):
        for entry in self.values():
            entry._pref_override = pref_override

    def not_pref(self, conditions, opt):
        return self[conditions].pref != opt


EQUIP_MANAGERS = {}


def get_equip_manager(advname, variant=None):
    try:
        return EQUIP_MANAGERS[advname][variant]
    except KeyError:
        manager = EquipManager(advname, variant)
        try:
            EQUIP_MANAGERS[advname][variant] = manager
        except KeyError:
            EQUIP_MANAGERS[advname] = {variant: manager}
        return manager


def _test_equip(advname, confs=None):
    import core.simulate

    advmodule, advname, variant = core.simulate.load_adv_module(advname)
    equip_manager = get_equip_manager(advname)
    for conf in confs:
        adv, real_d, _ = core.simulate.test(advname, advmodule, conf, 180, 5)
        equip_manager.accept_new_entry(adv, real_d)
    return equip_manager


OLD_KEY_TO_COND = {
    "base": ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, MonoCondition.ANY)),
    "buffer": ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, MonoCondition.ANY)),
    "affliction": ConditionTuple((AfflictionCondition.ALWAYS, SituationCondition.NORMAL, MonoCondition.ANY)),
    "noaffliction": ConditionTuple((AfflictionCondition.IMMUNE, SituationCondition.NORMAL, MonoCondition.ANY)),
    "mono_base": ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, MonoCondition.MONO)),
    "mono_buffer": ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, MonoCondition.MONO)),
    "mono_affliction": ConditionTuple((AfflictionCondition.ALWAYS, SituationCondition.NORMAL, MonoCondition.MONO)),
    "mono_noaffliction": ConditionTuple((AfflictionCondition.IMMUNE, SituationCondition.NORMAL, MonoCondition.MONO)),
}


def convert_from_existing(advname):
    import core.simulate

    old_equip = load_json(f"equip/{advname}.json")
    old_180s = old_equip["180"]
    advmodule, advname, variant = core.simulate.load_adv_module(advname)
    equip_manager = get_equip_manager(advname)
    for key, conf in old_180s.items():
        if isinstance(conf, str):
            continue
        condition = OLD_KEY_TO_COND[key]
        if DEBUG:
            print(f"CONVERT {key} -> {condition}")
        if condition.mono == MonoCondition.MONO:
            try:
                conf = {**old_180s[key.split("_")[-1]], **conf}
            except KeyError:
                continue
        conf.update(condition.get_conf())
        pprint(conf)
        adv, real_d, _ = core.simulate.test(advname, advmodule, conf, 180, 5)
        equip_manager.accept_new_entry(adv, real_d)
        print("=" * 100)


if __name__ == "__main__":
    convert_from_existing("Elisanne")