from pprint import pprint
from copy import deepcopy
import os

from conf import (
    load_equip_json,
    save_equip_json,
    DURATIONS,
    ELE_AFFLICT,
    mono_elecoabs,
    load_adv_json,
    list_advs,
)
import core.simulate

BANNED_PRINTS = ("Witchs_Kitchen", "Berry_Lovable_Friends", "Happier_Times")
BANNED_SHARES = ("Durant", "Yue")
ABNORMAL_COND = (
    "sim_buffbot",
    "dragonbattle",
    "berserk",
    "classbane",
    "hp",
    "dumb",
    "afflict_res",
    "fleet",
)
BUFFER_TDPS_THRESHOLD = 40000
BUFFER_TEAM_THRESHOLD = 1.6
TDPS_WEIGHT = 15000


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
    def acceptable(entry, ele=None):
        return isinstance(entry, EquipEntry)

    def same_build(self, other):
        return all((self.get(k) == other.get(k) for k in EquipEntry.CONF_KEYS))

    def same_build_different_dps(self, other):
        same_build = all((self.get(k) == other.get(k) for k in EquipEntry.CONF_KEYS))
        different_dps = any((self.get(k) != other.get(k) for k in EquipEntry.META_KEYS))
        return same_build and different_dps

    @staticmethod
    def weight(entry):
        return entry["dps"] + entry["team"] * TDPS_WEIGHT

    def better_than(self, other):
        return self.weight(self) > self.weight(other)

    def update_threshold(self, other):
        if self["team"] != other["team"]:
            self["tdps"] = None
            other["tdps"] = (self["dps"] - other["dps"]) / (
                other["team"] - self["team"]
            )
        else:
            self["tdps"] = None
            other["tdps"] = None


def build_entry_from_sim(entryclass, adv, real_d):
    ndps = sum(map(lambda v: sum(v.values()), adv.logs.damage.values())) / real_d
    nteam = adv.logs.team_buff / real_d
    new_equip = {
        "dps": ndps,
        "team": nteam,
        "tdps": None,
        "slots.a": adv.slots.a.qual_lst,
        "slots.d": adv.slots.d.qual,
    }
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


class BaseEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return not adv.sim_afflict and EquipEntry.eligible(adv)


class BufferEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        return not adv.sim_afflict and EquipEntry.eligible(adv)

    @staticmethod
    def acceptable(entry, ele=None):
        return entry["team"] and EquipEntry.acceptable(entry)

    def better_than(self, other):
        return self["team"] > other["team"] or (
            self["team"] == other["team"] and self["dps"] > other["dps"]
        )


class AfflictionEntry(EquipEntry):
    @staticmethod
    def eligible(adv):
        eleaff = ELE_AFFLICT[adv.slots.c.ele]
        return (
            adv.sim_afflict == {eleaff} and adv.conf_init.sim_afflict[eleaff] == 1
        ) and EquipEntry.eligible(adv)


def all_monoele_coabs(entry, ele):
    return all((coab in mono_elecoabs[ele] for coab in entry["coabs"]))


class MonoBaseEntry(BaseEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and BaseEntry.acceptable(entry)


class MonoBufferEntry(BufferEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and BufferEntry.acceptable(entry)


class MonoAfflictionEntry(AfflictionEntry):
    @staticmethod
    def acceptable(entry, ele):
        return all_monoele_coabs(entry, ele) and AfflictionEntry.acceptable(entry)


EQUIP_ENTRY_MAP = {
    "base": BaseEntry,
    "buffer": BufferEntry,
    "affliction": AfflictionEntry,
    # 'affbuff' ?
    "mono_base": MonoBaseEntry,
    "mono_buffer": MonoBufferEntry,
    "mono_affliction": MonoAfflictionEntry,
}
KICK_TO = {
    "base": ("buffer", "mono_base"),
    "buffer": ("mono_buffer",),
    "affliction": ("mono_affliction",),
}
THRESHOLD_RELATION = (
    ("base", "buffer", "pref"),
    ("mono_base", "mono_buffer", "mono_pref"),
)


class EquipManager(dict):
    def __init__(self, advname, debug=False):
        self.advname = advname
        if debug:
            super().__init__({})
            self.debug = True
        else:
            super().__init__(load_equip_json(advname))
            self.debug = False
        self.pref = None
        for duration, dequip in self.items():
            for kind, entry in dequip.items():
                try:
                    dequip[kind] = EQUIP_ENTRY_MAP[kind](entry)
                except KeyError:
                    if kind == "pref":
                        self.pref = entry

    def accept_new_entry(self, adv, real_d):
        if self.advname != adv.name:
            raise RuntimeError(f"adv/equip name mismatch {self.advname} != {adv.name}")

        duration = int(adv.duration)
        print(duration, DURATIONS)
        if duration not in DURATIONS:
            return

        duration = str(duration)
        kicked_entries = []
        need_write = False
        if duration not in self:
            self[duration] = {"pref": "base", "mono_pref": "mono_base"}

        # first pass
        for kind, entryclass in EQUIP_ENTRY_MAP.items():
            if not entryclass.eligible(adv):
                continue
            new_entry = build_entry_from_sim(entryclass, adv, real_d)
            if not entryclass.acceptable(new_entry, adv.slots.c.ele):
                continue
            if self.debug:
                print("~" * 60)
                print(kind, adv.sim_afflict)
                pprint(new_entry)
            try:
                current_entry = self[duration][kind]
            except KeyError:
                self[duration][kind] = new_entry
                need_write = True
                if self.debug:
                    print("fill empty slot")
                continue
            if current_entry.same_build_different_dps(
                new_entry
            ) or not current_entry.better_than(new_entry):
                if self.debug:
                    print("better than existing/same build different dps")
                self[duration][kind] = deepcopy(new_entry)
                need_write = True
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
                self[duration][basekind].update_threshold(self[duration][buffkind])
                try:
                    if (
                        self[duration][buffkind]["team"] > BUFFER_TEAM_THRESHOLD
                        or self[duration][buffkind]["tdps"] < BUFFER_TDPS_THRESHOLD
                    ):
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
        conf = deepcopy(conf)
        if kind in ("affliction", "mono_affliction"):
            conf[f"sim_afflict.{ELE_AFFLICT[element]}"] = 1
        with open(os.devnull, "w") as output:
            run_res = core.simulate.test(
                self.advname, adv_module, conf, int(duration), output=output
            )
        adv = run_res[0][0]
        real_d = run_res[0][1]
        new_entry = build_entry_from_sim(EQUIP_ENTRY_MAP[kind], adv, real_d)
        if not do_compare or not self[duration][kind].better_than(new_entry):
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
                self.repair_entry(
                    adv_module, element, self[duration][kind], duration, kind
                )

        for duration in list(self.keys()):
            for kind in list(self[duration].keys()):
                # if duration != '180':
                #     try:
                #         self.repair_entry(adv_module, element, self['180'][kind], duration, kind, do_compare=True)
                #     except KeyError:
                #         pass
                # for affkind, basekind in (('affliction', 'base'), ('mono_affliction', 'mono_base')):
                #     try:
                #         self.repair_entry(adv_module, element, self[duration][basekind], duration, affkind, do_compare=True)
                #     except KeyError:
                #         pass
                for basekind in ("base", "buffer", "affliction"):
                    monokind = f"mono_{basekind}"
                    if not basekind in self[duration]:
                        continue
                    if not EQUIP_ENTRY_MAP[monokind].acceptable(
                        self[duration][basekind], element
                    ):
                        continue
                    try:
                        current_entry = self[duration][monokind]
                        if not current_entry.better_than(self[duration][basekind]):
                            self[duration][monokind] = deepcopy(
                                self[duration][basekind]
                            )
                    except KeyError:
                        self[duration][monokind] = deepcopy(self[duration][basekind])

            self.update_tdps_threshold(duration)

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
    return {advname: EquipManager(advname) for advname in list_advs()}


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
    test_repair()
