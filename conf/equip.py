import json
import itertools
import os
import sys
import shutil
from enum import Enum
from pprint import pprint

from core.afflic import AFFLICT_LIST
from conf import (
    SKIP_VARIANT,
    get_conf_json_path,
    ELE_AFFLICT,
    list_advs,
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
BUILD_META_KEY = "EQMT"

DEBUG = False


def dprint(msg, pretty=False):
    if DEBUG:
        if pretty:
            pprint(msg)
        else:
            print(msg, flush=True)


class ValueEnum(Enum):
    def __str__(self):
        return str(self.value)


class AfflictionCondition(ValueEnum):
    SELF = "SELF"
    ALWAYS = "ALWAYS"
    IMMUNE = "IMMUNE"

    @classmethod
    def get_condition(cls, adv):
        if all((value >= 3 for value in adv.afflics.get_resist().values())):
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

    def aff_to(self, value):
        _, sit, mono = self
        return ConditionTuple((value, sit, mono))

    def sit_to(self, value):
        aff, _, mono = self
        return ConditionTuple((aff, value, mono))

    def mono_to(self, value):
        aff, sit, _ = self
        return ConditionTuple((aff, sit, value))

    def get_conf(self):
        conf = {}
        for value in self:
            conf.update(value.get_conf())
        return conf


ALL_COND_ENUMS = (AfflictionCondition, SituationCondition, MonoCondition)
DEFAULT_CONDITONS = ConditionTuple((AfflictionCondition.SELF, SituationCondition.NORMAL, MonoCondition.ANY))


def dps_weight(entry):
    return entry.dps + entry.team * TDPS_WEIGHT


class OpimizationMode(ValueEnum):
    PERSONAL = "PERSONAL"
    TEAMBUFF = "TEAMBUFF"


def build_equip_condition(equip):
    if equip is None:
        return DEFAULT_CONDITONS, None
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
    return same_build(entry_a, entry_b) and entry_a.equip_metadata != entry_b.equip_metadata


def same_build_same_dps(entry_a, entry_b):
    return same_build(entry_a, entry_b) and entry_a.equip_metadata == entry_b.equip_metadata


def compare_build_personal(entry_a, entry_b):
    return dps_weight(entry_a) >= dps_weight(entry_b)


def compare_build_teambuff(entry_a, entry_b):
    return entry_a.team > 0 and entry_a.team > entry_b.team or (round(entry_a.team, 5) == round(entry_b.team, 5) and entry_a.dps >= entry_b.dps)


OPT_COMPARE = {
    OpimizationMode.PERSONAL: compare_build_personal,
    OpimizationMode.TEAMBUFF: compare_build_teambuff,
}
OPT_KICK = {
    OpimizationMode.PERSONAL: OpimizationMode.TEAMBUFF,
    OpimizationMode.TEAMBUFF: OpimizationMode.PERSONAL,
}


class EquipBuild(dict):
    @property
    def dps(self):
        return self[BUILD_META_KEY]["dps"]

    @property
    def team(self):
        return self[BUILD_META_KEY]["team"]

    @property
    def noaff(self):
        return self[BUILD_META_KEY]["noaff"]

    @property
    def nihil(self):
        return self[BUILD_META_KEY]["nihil"]

    @property
    def equip_metadata(self):
        return self[BUILD_META_KEY]


def build_from_sim(adv, real_d):
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    build = {BUILD_META_KEY: {"dps": ndps, "team": nteam, "noaff": not bool(adv.uses_affliction()), "nihil": adv.nihilism}}
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
    return EquipBuild(build)


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
    if not all([not ss in BANNED_SHARES for ss in adv.skillshare_list]):
        return False, "Using a banned share"
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
                try:
                    converted = {}
                    for opt in OpimizationMode:
                        try:
                            converted[opt] = ConditionTuple.from_str(v["partial"][opt.name])
                        except KeyError:
                            converted[opt] = None
                    v["partial"] = converted
                except KeyError:
                    pass
                self[k].update(v)
            else:
                self[OpimizationMode(k)] = EquipBuild(v)

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

    @property
    def pref_override(self):
        return self._pref_override

    @pref_override.setter
    def pref_override(self, pref):
        self._pref_override = pref

    def get_partial_base(self, opt):
        based_on = self["META"]["partial"][opt]
        if self._aff_to_self and based_on == self._aff_to_self._conditions:
            base_build = self._aff_to_self.get_build(opt, flexible_opt=False)
            if base_build:
                return base_build, based_on
        if self._mono_to_any and based_on == self._mono_to_any._conditions:
            base_build = self._mono_to_any.get_build(opt, flexible_opt=False)
            if base_build:
                return base_build, based_on
        return None, None

    def get_build(self, opt, with_conditions=False, strict=False, flexible_opt=False):
        original_opt = opt
        while True:
            build = self[opt]
            base_build, based_on = self.get_partial_base(opt)
            if base_build:
                if build:
                    dprint(f"RESTORE FROM PARTIAL {based_on}")
                    if with_conditions:
                        conditions = based_on if set(build.keys()) == {BUILD_META_KEY} else self._conditions
                        return EquipBuild({**base_build, **build}), conditions
                    return EquipBuild({**base_build, **build})
                elif not strict:
                    if with_conditions:
                        return base_build, based_on
                    return base_build
            if not strict and not build and self._default:
                return self._default.get_build(opt, with_conditions=with_conditions, flexible_opt=flexible_opt)
            if build or original_opt != opt or not flexible_opt:
                break
            opt = OPT_KICK[opt]
        if with_conditions:
            return build, self._conditions
        return build

    def builds(self, skip_none=False, **kwargs):
        for opt in OpimizationMode:
            build = self.get_build(opt, **kwargs)
            if kwargs.get("with_conditions"):
                if not skip_none or not build[0] is None:
                    yield opt, build
            elif not skip_none or not build is None:
                yield opt, build

    @property
    def preferred(self):
        return self.get_build(self.pref, with_conditions=True, flexible_opt=True)

    @property
    def empty(self):
        return not any((self[opt] for opt in OpimizationMode))

    @property
    def dps_only(self):
        return all((set(self[opt].keys()) == {BUILD_META_KEY} for opt in OpimizationMode))

    def update_meta(self):
        dprint(f"UPDATE META {self._conditions}")
        personal_build = self.get_build(OpimizationMode.PERSONAL)
        teambuff_build = self.get_build(OpimizationMode.TEAMBUFF)
        if not teambuff_build:
            dprint("NO TEAMBUFF BUILD")
            self.tdps = None
            self.pref = OpimizationMode.PERSONAL
            return
        if not personal_build:
            dprint("NO PERSONAL BUILD")
            self.tdps = None
            self.pref = OpimizationMode.TEAMBUFF
            return

        if personal_build.team < teambuff_build.team:
            self.tdps = (personal_build.dps - teambuff_build.dps) / (teambuff_build.team - personal_build.team)
        else:
            self.tdps = None
            if same_build(personal_build, teambuff_build) and self._default is not None:
                self[OpimizationMode.TEAMBUFF] = None

        if teambuff_build.team > BUFFER_TEAM_THRESHOLD or (self.tdps is not None and self.tdps < BUFFER_TDPS_THRESHOLD):
            self.pref = OpimizationMode.TEAMBUFF
        else:
            self.pref = OpimizationMode.PERSONAL

        dprint(f"NEW tdps {self.tdps}, pref {self.pref}")

    def set_build(self, opt, build):
        dprint(f"ACCEPTED {self._conditions}.{opt}")
        self[opt] = EquipBuild({**build})
        self["META"]["partial"][opt] = None

    def set_build_diff(self, opt, build_diff, based_on):
        dprint(f"DIFF ONLY {self._conditions}.{opt} BASED ON {based_on}, {build_diff}")
        self[opt] = EquipBuild({BUILD_META_KEY: self[opt][BUILD_META_KEY], **build_diff})
        self["META"]["partial"][opt] = based_on

    def delete_build(self, opt, based_on=None):
        dprint(f"DELETED {self._conditions}.{opt}")
        self[opt] = None
        self["META"]["partial"][opt] = based_on

    def accept_new_build(self, new_build, adv):
        dprint("-" * 100)
        dprint(f"CHECKING {self._conditions}:")
        dprint(new_build, pretty=True)

        changed = False

        # in the case where we have aff -> self downgrading and this sim did not use afflictions, send build off to that first
        if self._aff_to_self and new_build.noaff:
            dprint(f"PASSED from {self._conditions} to {self._aff_to_self._conditions} (_aff_to_self)")
            changed = self._aff_to_self.accept_new_build(new_build, adv) or changed

        # check against current builds
        for opt, existing_buildcond in self.builds(strict=True, with_conditions=True):
            existing_build, existing_cond = existing_buildcond
            if (
                not existing_build
                or (existing_cond == self._conditions and same_build_different_dps(new_build, existing_build))
                or OPT_COMPARE[opt](new_build, existing_build)
            ):
                if existing_build:
                    dprint(f"EXISTING DPS {existing_build.dps}, TEAM {existing_build.team}")
                    dprint(f"NEW DPS {new_build.dps}, TEAM {new_build.team}")
                else:
                    dprint("NO EXISTING BUILD")
                self.set_build(opt, new_build)
                changed = True

        # check against downgrade targets
        if self._mono_to_any:
            dprint(f"PASSED from {self._conditions} to {self._mono_to_any._conditions} (_mono_to_any)")
            changed = self._mono_to_any.accept_new_build(new_build, adv) or changed
            for opt, ref_buildcond in self._mono_to_any.builds(skip_none=True, with_conditions=True):
                if not self[opt]:
                    continue
                ref_build, ref_cond = ref_buildcond
                # check if any build is also a mono build, and is equal/better than this build
                if all_monoele_coabs(adv.slots.c.ele, ref_build["coabs"]) and OPT_COMPARE[opt](ref_build, self[opt]):
                    dprint("ANY IS ALSO MONOELE")
                    self.delete_build(opt, ref_cond)
                    changed = True
                    continue
                # check if the builds are different, and store only the parts that are not the same
                build_diff = difference_of_builds(ref_build, self[opt])
                if not build_diff:
                    dprint("SAME MONOELE")
                    self.delete_build(opt, ref_cond)
                    changed = True
                    continue
                self.set_build_diff(opt, build_diff, ref_cond)

        if self._aff_to_self:
            # always aff
            if self._conditions.aff == AfflictionCondition.ALWAYS:
                for opt, ref_buildcond in self._aff_to_self.builds(skip_none=True, with_conditions=True):
                    ref_build, ref_cond = ref_buildcond
                    if self[opt]:
                        # self build is equal or better than aff build
                        if OPT_COMPARE[opt](ref_build, self[opt]):
                            dprint("SELF BETTER THAN ALWAYS AFF")
                            self.delete_build(opt, ref_cond)
                        else:
                            # save the differences only
                            build_diff = difference_of_builds(ref_build, self[opt])
                            self.set_build_diff(opt, build_diff, ref_cond)
                        changed = True
            # immune aff
            elif self._conditions.aff == AfflictionCondition.IMMUNE:
                for opt, ref_buildcond in self._aff_to_self.builds(skip_none=True, with_conditions=True):
                    ref_build, ref_cond = ref_buildcond
                    if self[opt]:
                        # self build is identical or ref build is no aff and better
                        if same_build_same_dps(ref_build, self[opt]) or (ref_build.noaff and OPT_COMPARE[opt](ref_build, self[opt])):
                            dprint("SELF BETTER THAN IMMUNE AFF")
                            self.delete_build(opt, ref_cond)
                            continue
                        else:
                            # save the differences only
                            build_diff = difference_of_builds(ref_build, self[opt])
                            self.set_build_diff(opt, build_diff, ref_cond)
                        changed = True

        # # check against default
        # if self._default:
        #     for opt, reference_build in self._default.builds(skip_none=True):
        #         if self[opt] and same_build(reference_build, self[opt]):
        #             self.delete_build(opt)
        #             changed = True

        if changed:
            self.update_meta()
        dprint("-" * 100)
        return changed


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
    EQUIP_DIR = "equip"

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
        for conditions in map(ConditionTuple, itertools.product(*ALL_COND_ENUMS)):
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
                value._aff_to_self = self.get(key.aff_to(AfflictionCondition.SELF))
            if key.mono == MonoCondition.MONO:
                value._mono_to_any = self.get(key.mono_to(MonoCondition.ANY))
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
            # return json.dump(encodable(self), f, ensure_ascii=False, default=str, separators=(",", ":"))
            return json.dump(encodable(self), f, ensure_ascii=False, default=str, indent=2)

    def display_json(self):
        return json.dumps(encodable(self), ensure_ascii=False, default=str, indent=2)

    def accept_new_entry(self, adv, real_d):
        valid, failure = validate_sim(adv)
        if not valid:
            dprint(f"INVALID SIM: {failure!r}")
            return
        try:
            conditions = ConditionTuple((cond_enum.get_condition(adv) for cond_enum in ALL_COND_ENUMS))
            dprint(f"ELIGABLE FOR {conditions}")
        except ValueError:
            return
        new_build = build_from_sim(adv, real_d)
        if conditions.aff == AfflictionCondition.SELF and new_build.noaff:
            for aff in (AfflictionCondition.IMMUNE, AfflictionCondition.ALWAYS):
                changed = self[conditions.aff_to(aff)].accept_new_build(new_build, adv)
        else:
            changed = self[conditions].accept_new_build(new_build, adv)
        if changed:
            self.save_equip_json()
        return new_build

    def accept_new_entry_with_faith(self, adv, real_d, conditions, opt):
        valid, failure = validate_sim(adv)
        if not valid:
            self[conditions].delete_build(opt)
            return
        self[conditions][opt] = build_from_sim(adv, real_d)
        return self[conditions]

    def repair_entries(self, advmodule):
        import core.simulate

        for opt in OpimizationMode:
            for conditions, entry in self.items():
                if entry[opt] is None:
                    continue
                # repair this condition
                adv, real_d = core.simulate.test(
                    self._advname,
                    advmodule,
                    duration=180,
                    verbose=4,
                    equip_conditions=conditions,
                    opt_mode=opt,
                )
                self.accept_new_entry_with_faith(adv, real_d, conditions, opt)
                # check this build against all other aff conditions
                for aff in AfflictionCondition:
                    if aff == conditions.aff:
                        continue
                    affcond = conditions.aff_to(aff)
                    adv, real_d = core.simulate.test(
                        self._advname,
                        advmodule,
                        duration=180,
                        verbose=4,
                        conf=affcond.get_conf(),
                        equip_conditions=conditions,
                        opt_mode=opt,
                    )
                    self.accept_new_entry(adv, real_d)

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
        dprint(f"CONVERT {key} -> {condition}")
        if condition.mono == MonoCondition.MONO:
            try:
                conf = {**old_180s[key.split("_")[-1]], **conf}
            except KeyError:
                continue
        conf.update(condition.get_conf())
        dprint(conf, pretty=True)
        adv, real_d = core.simulate.test(advname, advmodule, conf, 180, 4)
        equip_manager.accept_new_entry(adv, real_d)
        dprint("=" * 100)
    dprint(equip_manager.display_json())


def sha256sum(filename):
    import hashlib

    if not os.path.exists(filename):
        return None
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def n_pass_test(advname):
    from time import monotonic

    new_equip_file = f"./conf/equip.new/{advname}.json"
    try:
        os.remove(new_equip_file)
    except FileNotFoundError:
        pass
    t_start = monotonic()
    equilibrium = 0
    max_equilibrium = 3
    convert_from_existing(advname)
    sha256 = sha256sum(new_equip_file)
    print(advname, end="\t", flush=True)
    while equilibrium < max_equilibrium:
        dprint("")
        dprint("=" * 100)
        dprint("")
        equilibrium += 1
        convert_from_existing(advname)
        next_sha256 = sha256sum(new_equip_file)
        if sha256 == next_sha256:
            break
        sha256 = next_sha256
    print(monotonic() - t_start, flush=True)
    if equilibrium == max_equilibrium and sha256 != next_sha256:
        print(f"Failed to achieve equilibrium for {advname}")
    else:
        dprint(f"It took {equilibrium} iterations to achieve equilibrium")
    # convert_from_existing(advname)
    # second_pass = sha256sum(new_equip_file)
    # if first_pass != second_pass:
    #     print(f"{advname} differed")


if __name__ == "__main__":
    # advname = sys.argv[1]
    # convert_from_existing(advname)
    # n_pass_test("alberius")
    # python deploy.py lea valerio gala_notte sophie_persona patia chelsea hunter_sarisse noelle hildegarde gala_chelle -c
    # advlist = ["lea", "valerio", "gala_notte", "sophie_persona", "patia", "chelsea", "hunter_sarisse", "noelle", "hildegarde", "gala_chelle"]
    for advname in list_advs():
        n_pass_test(advname)
