from pprint import pprint
from copy import deepcopy
import os

from conf import (
    load_equip_json,
    save_equip_json,
    DURATIONS,
    ELE_AFFLICT,
    mono_elecoabs,
    get_adv_coability,
    load_adv_json,
    list_advs,
)
import core.simulate
from core.afflic import Afflics, AFFLICT_LIST

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
    # defense reduction
    "Holywyrms_Advent",
)
BANNED_SHARES = ("Durant", "Yue")
ABNORMAL_COND = (
    "sim_buffbot",
    "dragonbattle",
    "berserk",
    "nihilism",
    "classbane",
    "hp",
    "dumb",
    "fleet",
)
BUFFER_TDPS_THRESHOLD = 40000
BUFFER_TEAM_THRESHOLD = 1.6
TDPS_WEIGHT = 15000
HAS_7SLOT = ("light",)
DEFAULT_MONO_COABS = {
    "flame": ("Blade", "Wand", "Dagger", "Bow"),
    "water": ("Blade", "Wand", "Dagger", "Bow"),
    "wind": ("Blade", "Mona", "Dragonyule_Xainfried", "Dagger"),
    "light": ("Blade", "Peony", "Wand", "Dagger"),
    "shadow": ("Blade", "Wand", "Dagger", "Bow"),
}


def equivalent(a, b):
    try:
        return set(a) == set(b)
    except (ValueError, TypeError):
        return a == b


def build_entry_from_sim(entryclass, adv, real_d, coab_only=False):
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    new_equip = {
        "dps": ndps,
        "team": nteam,
        "tdps": None,
    }
    if coab_only:
        new_equip["coabs"] = adv.slots.c.coab_list
        return entryclass(new_equip)
    new_equip["slots.a"] = adv.slots.a.qual_lst
    new_equip["slots.d"] = adv.slots.d.qual
    # if adv.slots.d.qual != adv.slots.DEFAULT_DRAGON[adv.slots.c.ele]:
    #     new_equip['slots.d'] = adv.slots.d.qual
    if adv.slots.w.qual != adv.slots.DEFAULT_WEAPON:
        new_equip["slots.w"] = adv.slots.w.qual
    acl_list = adv.conf.acl
    if not isinstance(acl_list, list):
        acl_list = [line.strip() for line in acl_list.split("\n") if line.strip()]
    new_equip["acl"] = acl_list
    new_equip["coabs"] = adv.slots.c.coab_list
    new_equip["share"] = adv.skillshare_list
    return entryclass(new_equip)


def filter_coab_only(entry):
    return {
        "dps": entry["dps"],
        "team": entry["team"],
        "tdps": entry["tdps"],
        "coabs": entry["coabs"],
    }


class EquipEntry(dict):
    CONF_KEYS = ("slots.a", "slots.d", "slots.w", "acl", "coabs", "share")
    META_KEYS = ("dps", "team")

    def __init__(self, equip):
        super().__init__(equip)

    @staticmethod
    def eligible(adv):
        adv.duration = int(adv.duration)
        return (
            adv.duration in DURATIONS
            and all([not k in adv.conf for k in ABNORMAL_COND])
            and all([not wp in BANNED_PRINTS for wp in adv.slots.a.qual_lst])
            and all([not ss in BANNED_SHARES for ss in adv.skillshare_list])
        )

    @staticmethod
    def standard_affres(adv):
        return adv.afflics.get_resist() == Afflics.RESIST_PROFILES[adv.slots.c.ele]

    @staticmethod
    def acceptable(entry, ele=None):
        if len(entry.get("slots.a", tuple())) > 5 and (ele not in HAS_7SLOT or entry.get("slots.w", "Agito") != "Agito"):
            return False
        if len(entry.get("coabs")) != 3:
            return False
        return isinstance(entry, EquipEntry)

    @classmethod
    def build_from_sim(cls, adv, real_d):
        return build_entry_from_sim(cls, adv, real_d)

    def same_build(self, other):
        return all((equivalent(self.get(k), other.get(k)) for k in EquipEntry.CONF_KEYS))

    def same_build_different_dps(self, other):
        same_build = self.same_build(other)
        different_dps = any((self.get(k) != other.get(k) for k in EquipEntry.META_KEYS))
        return same_build and different_dps

    @staticmethod
    def weight(entry):
        return entry["dps"] + entry["team"] * TDPS_WEIGHT

    def better_than(self, other):
        return self.weight(self) >= self.weight(other)

    def update_threshold(self, other, change_self=True):
        if self["team"] != other["team"]:
            if change_self:
                self["tdps"] = None
            other["tdps"] = (self["dps"] - other["dps"]) / (other["team"] - self["team"])
        else:
            if change_self:
                self["tdps"] = None
            other["tdps"] = None


class BaseEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return not adv.sim_afflict and EquipEntry.standard_affres(adv) and EquipEntry.eligible(adv)


class BufferEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return not adv.sim_afflict and EquipEntry.standard_affres(adv) and EquipEntry.eligible(adv)

    @staticmethod
    def acceptable(entry, ele=None):
        return entry["team"] and EquipEntry.acceptable(entry, ele)

    def better_than(self, other):
        return self["team"] > other["team"] or (round(self["team"], 5) == round(other["team"], 5) and self["dps"] > other["dps"])


class AfflictionEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return AfflictionEntry.onele_affliction(adv) and EquipEntry.standard_affres(adv) and EquipEntry.eligible(adv)

    @staticmethod
    def onele_affliction(adv):
        eleaff = ELE_AFFLICT[adv.slots.c.ele]
        return adv.sim_afflict == {eleaff} and adv.conf_init.sim_afflict[eleaff] == 1


class NoAfflictionEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return (NoAfflictionEntry.immune_affres(adv) or not adv.use_afflict) and EquipEntry.eligible(adv)

    @staticmethod
    def immune_affres(adv):
        affres = adv.afflics.get_resist()
        return all((value >= 300 for value in affres.values()))


def all_monoele_coabs(entry, ele):
    return all((coab in mono_elecoabs[ele] for coab in entry["coabs"]))


def filtered_monoele_coabs(entry, ele):
    entry = deepcopy(entry)
    entry["coabs"] = [coab for coab in entry["coabs"] if coab in mono_elecoabs[ele]]
    return entry


class MonoEntry(EquipEntry):
    @classmethod
    def build_from_sim(cls, adv, real_d):
        return build_entry_from_sim(cls, adv, real_d, coab_only=True)

    def same_build(self, other):
        return equivalent(self.get("coabs"), other.get("coabs"))


class MonoBaseEntry(BaseEntry, MonoEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and BaseEntry.acceptable(entry, ele)


class MonoBufferEntry(BufferEntry, MonoEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and BufferEntry.acceptable(entry, ele)


class MonoAfflictionEntry(AfflictionEntry, MonoEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and AfflictionEntry.acceptable(entry, ele)


class MonoNoAfflictionEntry(NoAfflictionEntry, MonoEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and NoAfflictionEntry.acceptable(entry, ele)


EQUIP_ENTRY_MAP = {
    "base": BaseEntry,
    "buffer": BufferEntry,
    "affliction": AfflictionEntry,
    "noaffliction": NoAfflictionEntry,
    # 'affbuff' ?
    "mono_base": MonoBaseEntry,
    "mono_buffer": MonoBufferEntry,
    "mono_affliction": MonoAfflictionEntry,
    "mono_noaffliction": MonoNoAfflictionEntry,
}
SKIP_IF_IDENTICAL = {
    "affliction": "base",
    "noaffliction": "base",
    "mono_affliction": "mono_base",
    "mono_noaffliction": "mono_base",
}
SKIP_IF_SAME_COAB = {
    "mono_base": "base",
    "mono_buffer": "buffer",
    "mono_affliction": "affliction",
    "mono_noaffliction": "noaffliction",
}
KICK_TO = {
    "base": ("buffer", "mono_base"),
    "buffer": ("mono_buffer",),
    "affliction": ("mono_affliction",),
    "noaffliction": ("mono_noaffliction",),
}
THRESHOLD_RELATION = (
    ("base", "buffer", "pref"),
    ("mono_base", "mono_buffer", "mono_pref"),
)


class EquipManager(dict):
    def __init__(self, advname, debug=False):
        self.advname = advname
        super().__init__(load_equip_json(advname))
        self.debug = debug
        self.pref = None
        for duration, dequip in self.items():
            for kind, entry in dequip.items():
                try:
                    dequip[kind] = EQUIP_ENTRY_MAP[kind](entry)
                except KeyError:
                    if kind == "pref":
                        self.pref = entry

    def check_skip_entry(self, new_entry, duration, kind, compare_map, need_write=False, do_compare=True):
        try:
            compare_entry = self[duration][compare_map[kind]]
            if new_entry.same_build(compare_entry):
                try:
                    if not do_compare or new_entry.better_than(self[duration][kind]):
                        del self[duration][kind]
                        need_write = True
                        if self.debug:
                            print(f"Remove identical [{kind}] and fall back to [{compare_map[kind]}]")
                except KeyError:
                    pass
                return True, need_write
        except KeyError:
            pass
        return False, need_write

    def accept_new_entry(self, adv, real_d):
        if self.advname != adv.name:
            raise RuntimeError(f"adv/equip name mismatch {self.advname} != {adv.name}")

        duration = int(adv.duration)
        if duration not in DURATIONS:
            return

        duration = str(duration)
        kicked_entries = []
        need_write = False
        if duration not in self:
            self[duration] = {"pref": "base", "mono_pref": "mono_base"}

        # first pass
        for kind, entryclass in EQUIP_ENTRY_MAP.items():
            if self.debug:
                print("~" * 60)
                print(f"{kind}")
            if not entryclass.eligible(adv):
                if self.debug:
                    print(f"not eligible")
                continue
            new_entry = entryclass.build_from_sim(adv, real_d)
            if self.debug:
                pprint(new_entry)
            if not entryclass.acceptable(new_entry, adv.slots.c.ele):
                if self.debug:
                    print(f"not acceptable")
                continue
            skip, need_write = self.check_skip_entry(new_entry, duration, kind, SKIP_IF_IDENTICAL, need_write=need_write)
            if skip:
                continue
            skip, need_write = self.check_skip_entry(new_entry, duration, kind, SKIP_IF_SAME_COAB, need_write=need_write)
            if skip:
                continue
            try:
                current_entry = self[duration][kind]
            except KeyError:
                self[duration][kind] = new_entry
                need_write = True
                if self.debug:
                    print(f"fill empty slot {duration, kind}")
                continue
            same_build_different_dps = current_entry.same_build_different_dps(new_entry)
            better_than = new_entry.better_than(current_entry)
            if same_build_different_dps or better_than:
                if self.debug:
                    print("better than existing/same build different dps")
                self[duration][kind] = deepcopy(new_entry)
                need_write = True
                if better_than:
                    try:
                        if self.debug:
                            print(f"kick to {KICK_TO[kind]}")
                        for kicked_kind in KICK_TO[kind]:
                            kicked_entries.append((kicked_kind, current_entry))
                    except KeyError:
                        pass

        # kicked entries
        for kind, kicked in kicked_entries:
            entryclass = EQUIP_ENTRY_MAP[kind]
            if not entryclass.acceptable(kicked, adv.slots.c.ele):
                continue
            if kind.startswith("mono_"):
                kicked = entryclass(filter_coab_only(kicked))
                skip, need_write = self.check_skip_entry(kicked, duration, kind, SKIP_IF_SAME_COAB, need_write=need_write)
                if skip:
                    continue
            else:
                kicked = entryclass(deepcopy(kicked))
            try:
                current_entry = self[duration][kind]
            except KeyError:
                self[duration][kind] = kicked
                need_write = True
                continue
            if not current_entry.better_than(kicked):
                self[duration][kind] = kicked
                need_write = True

        tdps_write = self.update_tdps_threshold(duration)
        need_write = need_write or tdps_write

        if not self.debug and need_write:
            save_equip_json(self.advname, self)

    def update_tdps_threshold(self, duration):
        need_write = False
        for basekind, buffkind, prefkey in THRESHOLD_RELATION:
            try:
                ckind = self[duration].get(prefkey)
                if basekind.startswith("mono_") and basekind not in self[duration]:
                    self[duration][basekind[5:]].update_threshold(self[duration][buffkind], change_self=False)
                else:
                    self[duration][basekind].update_threshold(self[duration][buffkind])
                try:
                    if self[duration][buffkind]["team"] > BUFFER_TEAM_THRESHOLD or self[duration][buffkind]["tdps"] < BUFFER_TDPS_THRESHOLD:
                        self[duration][prefkey] = buffkind
                    else:
                        self[duration][prefkey] = basekind
                except TypeError:
                    self[duration][prefkey] = basekind
                need_write = need_write or ckind != self[duration].get(prefkey)
            except KeyError:
                continue
        return need_write

    def repair_entry(self, adv_module, element, conf, duration, kind, do_compare=False):
        if self.debug:
            print("~" * 60)
            print(f"Repair {kind}")
            pprint(conf)
        conf = deepcopy(conf)
        if kind in ("affliction", "mono_affliction"):
            conf[f"sim_afflict.{ELE_AFFLICT[element]}"] = 1
        if kind in ("noaffliction", "mono_noaffliction"):
            for afflic in AFFLICT_LIST:
                conf[f"afflict_res.{afflic}"] = 999
        with open(os.devnull, "w") as output:
            run_res = core.simulate.test(self.advname, adv_module, conf, int(duration), output=output)
        adv = run_res[0][0]
        real_d = run_res[0][1]
        new_entry = EQUIP_ENTRY_MAP[kind].build_from_sim(adv, real_d)
        if not EQUIP_ENTRY_MAP[kind].acceptable(new_entry, element):
            try:
                del self[duration][kind]
            except KeyError:
                pass
            return
        if not do_compare or not kind in self[duration] or new_entry.better_than(self[duration][kind]):
            self[duration][kind] = new_entry

    def repair_entries(self):
        adv_module, _ = core.simulate.load_adv_module(self.advname)
        element = load_adv_json(self.advname)["c"]["ele"]

        for duration in list(self.keys()):
            if not int(duration) in DURATIONS:
                del self[duration]

        for duration in list(self.keys()):
            for kind in list(self[duration].keys()):
                if kind.endswith("pref"):
                    continue
                if self.check_skip_entry(self[duration][kind], duration, kind, SKIP_IF_IDENTICAL, do_compare=False)[0]:
                    continue
                if self.check_skip_entry(self[duration][kind], duration, kind, SKIP_IF_SAME_COAB, do_compare=False)[0]:
                    continue
                self.repair_entry(adv_module, element, self[duration][kind], duration, kind)

        for duration in list(self.keys()):
            for basekind in ("base", "buffer", "affliction", "noaffliction"):
                monokind = f"mono_{basekind}"
                if not basekind in self[duration]:
                    try:
                        del self[duration][monokind]
                    except KeyError:
                        continue
                    continue
                if not EQUIP_ENTRY_MAP[monokind].acceptable(self[duration][basekind], element):
                    if monokind not in self[duration]:
                        # try auto populate
                        filtered_entry = filtered_monoele_coabs(self[duration][basekind], element)
                        if len(filtered_entry["coabs"]) == 3:
                            # same amount of coab, no need to populate
                            continue
                        advcoabs = get_adv_coability(self.advname)
                        for coab in DEFAULT_MONO_COABS[element]:
                            if len(filtered_entry["coabs"]) == 3:
                                break
                            if coab not in filtered_entry["coabs"] and coab not in advcoabs:
                                filtered_entry["coabs"].append(coab)
                        self.repair_entry(adv_module, element, filtered_entry, duration, monokind)
                    continue
                # try:
                #     current_entry = self[duration][monokind]
                #     if not current_entry.better_than(self[duration][basekind]):
                #         self[duration][monokind] = EQUIP_ENTRY_MAP[monokind](filter_coab_only(self[duration][basekind]))
                # except KeyError:
                #     self[duration][monokind] = EQUIP_ENTRY_MAP[monokind](filter_coab_only(self[duration][basekind]))

            self.update_tdps_threshold(duration)

        if not self.debug:
            save_equip_json(self.advname, self)

    def get_conf(self, duration, equip_key, mono):
        duration = str(int(duration))
        if not duration in self:
            duration = "180"
            if not duration in self:
                return None, None
        equip_d = self[duration]
        if equip_key is None:
            if mono:
                equip_key = equip_d.get("mono_pref", "mono_base")
                if equip_key not in equip_d:
                    equip_key = equip_d.get("pref", "base")
            else:
                equip_key = equip_d.get("pref", "base")
        if mono and not equip_key.startswith("mono_"):
            equip_key = f"mono_{equip_key}"
        if not equip_key in equip_d:
            return equip_d.get("base", None), None
        if equip_key.startswith("mono"):
            _, base_key = equip_key.split("_")
            full_equip = {}
            full_equip.update(equip_d[base_key])
            full_equip.update(equip_d[equip_key])
            return full_equip, equip_key
        else:
            return equip_d[equip_key], equip_key

    def has_different_mono(self, duration, kind):
        duration = str(int(duration))
        monokind = f"mono_{kind}"
        if not monokind in self[duration]:
            return False
        try:
            return not self[duration][kind].same_build(self[duration][monokind])
        except KeyError:
            return False


def initialize_equip_managers():
    return {advname: EquipManager(advname, debug=False) for advname in list_advs()}


def _test_equip(advname, confs):
    adv_module, advname = core.simulate.load_adv_module(advname)
    equip_manager = EquipManager(advname, debug=True)
    for conf in confs:
        run_res = core.simulate.test(advname, adv_module, conf, 180)
        adv = run_res[0][0]
        real_d = run_res[0][1]
        equip_manager.accept_new_entry(adv, real_d)
    return equip_manager


def test_equip_simple():
    basic_conf = {
        "slots.a": [
            "Candy_Couriers",
            "Me_and_My_Bestie",
            "Memory_of_a_Friend",
            "The_Plaguebringer",
            "To_the_Extreme",
        ],
        "slots.d": "Gala_Mars",
        "acl": [
            "`dragon(s-s)",
            "`s3, not buff(s3) and x=5",
            "`s1",
            "`s4,cancel",
            "`s2, x=5",
        ],
        "coabs": ["Blade", "Joe", "Marth"],
        "share": ["Weapon", "Durant"],
    }
    higher_team_conf = {**basic_conf, "share": ["Weapon", "Karl"]}
    higher_dps_conf = {**basic_conf, "share": ["Weapon", "Formal_Joachim"]}
    _test_equip("Xania", (basic_conf, higher_team_conf))


def test_equip_afflictions():
    basic_conf = {
        "slots.a": [
            "An_Ancient_Oath",
            "Dragon_and_Tamer",
            "Memory_of_a_Friend",
            "Entwined_Flames",
            "The_Plaguebringer",
        ],
        "slots.d": "Gala_Cat_Sith",
        "acl": [
            "`fs, x=5",
            "`s3, not buff(s3)",
            "`s2",
            "`s4",
            "`dragon(c3-s-end), cancel",
            "`s1(all)",
        ],
        "coabs": ["Ieyasu", "Wand", "Forte"],
        "share": ["Weapon", "Gala_Mym"],
    }
    basic_on_conf = {**basic_conf, "sim_afflict": {"poison": 1}}
    afflic_conf = {
        "slots.a": [
            "An_Ancient_Oath",
            "Dragon_and_Tamer",
            "Memory_of_a_Friend",
            "Dueling_Dancers",
            "The_Plaguebringer",
        ],
        "slots.d": "Gala_Cat_Sith",
        "acl": [
            "`dragon(c3-s-end), s4",
            "`s3, not buff(s3)",
            "`s2",
            "`s4, x=5 or fsc",
            "`s1(all), cancel or s",
            "`fs, x=5",
        ],
        "coabs": ["Ieyasu", "Wand", "Forte"],
        "share": ["Weapon", "Gala_Mym"],
    }
    afflic_on_conf = {**afflic_conf, "sim_afflict": {"poison": 1}}
    _test_equip("Lathna", (afflic_conf, basic_conf, afflic_on_conf, basic_on_conf))


def test_equip_monoele():
    base_conf = {
        "slots.a": [
            "A_Man_Unchanging",
            "Memory_of_a_Friend",
            "Moonlight_Party",
            "From_Whence_He_Comes",
            "Bellathorna",
        ],
        "slots.d": "Epimetheus",
        "acl": ["`dragon(s), s=1", "`s3, not buff(s3)", "`s1", "`s2", "`s4, x=5"],
        "coabs": ["Axe2", "Dagger2", "Tobias"],
        "share": ["Weapon", "Formal_Joachim"],
    }
    monoele_conf = {
        "slots.a": [
            "A_Man_Unchanging",
            "Memory_of_a_Friend",
            "Moonlight_Party",
            "From_Whence_He_Comes",
            "Bellathorna",
        ],
        "slots.d": "Epimetheus",
        "acl": ["`dragon(s), s=1", "`s3, not buff(s3)", "`s1", "`s2", "`s4, x=5"],
        "coabs": ["Dagger", "Forte", "Cleo"],
        "share": ["Weapon", "Gala_Mym"],
    }
    _test_equip("Durant", (monoele_conf, base_conf))


def test_repair():
    equip_manager = EquipManager("Aeleen")
    equip_manager.debug = True
    equip_manager.repair_entries()


if __name__ == "__main__":
    # test_repair()
    print(get_adv_coability("Peony"))
