from itertools import chain
from collections import defaultdict, namedtuple
import html

from conf import (
    load_json,
    wyrmprints,
    weapons,
    dragons,
    elecoabs,
    alias,
    ELEMENTS,
    WEAPON_TYPES,
    subclass_dict,
    get_icon,
)
from core.config import Conf
from core.ability import ability_dict


class SlotBase:
    KIND = "s"
    AUGMENTS = 0

    def __init__(self, conf, qual=None):
        self.conf = conf
        self.qual = qual
        self.att_augment = self.AUGMENTS
        self.hp_augment = self.AUGMENTS

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self.conf.name

    @property
    def escaped(self):
        return html.escape(self.conf.name).replace(",", "&#44;")

    @property
    def icon(self):
        return self.conf.icon

    def name_icon(self):
        return {
            "name": self.escaped,
            "icon": self.icon,
        }

    @property
    def att(self):
        return self.conf.att + self.att_augment

    @property
    def hp(self):
        return self.conf.hp + self.hp_augment

    @property
    def ab(self):
        if self.conf["a"]:
            return self.conf.a
        return []

    def oninit(self, adv):
        pass


class CharaBase(SlotBase):
    AUGMENTS = 100
    FORT = load_json("fort.json")
    # album_false album_true None
    FORT_KEY = "album_false"

    MAX_COAB = 3  # max allowed coab, excluding self

    def __init__(self, conf, qual=None):
        super().__init__(conf, qual)
        self.coabs = {}
        self.coab_list = []
        self.coab_qual = None
        self.valid_coabs = elecoabs[self.ele]
        try:
            self.coabs[self.qual] = self.valid_coabs[self.qual]
            self.coab_qual = self.qual
        except KeyError:
            try:
                self.coab_qual = self.wt.capitalize()
                self.coabs[self.coab_qual] = self.valid_coabs[self.coab_qual]
            except KeyError:
                pass
        self._chain_ctime = 0
        self._ctime_coabs = []
        self._need_ctime = 0

        self._healing_coabs = []
        self._need_healing = False

        self._regen_coabs = []
        self._need_regen = False

        self._bufftime_coabs = []
        self._need_bufftime = False

    def set_coab_list(self, coab_list):
        for name in coab_list:
            try:
                self.coabs[name] = self.valid_coabs[name]
            except KeyError:
                raise ValueError(f"No such coability: {name}")

    def update_req_ctime(self, delta, ctime):
        self._need_ctime = max(self._need_ctime, delta - (ctime - self._chain_ctime))

    def set_need_healing(self):
        self._need_healing = True

    def set_need_regen(self):
        self._need_regen = True

    def set_need_bufftime(self):
        self._need_bufftime = True

    def downgrade_one_coab(self, key, coab):
        try:
            self.coab_list.remove(key)
            del self.coabs[key]
            category = coab["category"]
            self.coabs[category] = self.valid_coabs[category]
            self.coab_list.append(category)
        except (ValueError, KeyError):
            pass

    def downgrade_coabs(self):
        for ctime_value, key, coab in sorted(self._ctime_coabs, reverse=True):
            if self._chain_ctime - ctime_value < self._need_ctime:
                continue
            self.downgrade_one_coab(key, coab)
            self._chain_ctime -= ctime_value

        for flag, coab_list in (
            (self._need_healing, self._healing_coabs),
            (self._need_regen, self._regen_coabs),
            (self._need_bufftime, self._bufftime_coabs),
        ):
            if not flag:
                for key, coab in coab_list:
                    self.downgrade_one_coab(key, coab)
        self.coab_list = sorted(self.coab_list)

    @property
    def ab(self):
        full_ab = list(super().ab)
        ex_ab = {}
        max_coabs = CharaBase.MAX_COAB
        coabs = list(self.coabs.items())
        self.coabs = {}
        self.coab_list = []
        seen_base_id = {self.icon.split("_")[0]}
        for key, coab in coabs:
            # alt check
            if key != self.coab_qual:
                icon = get_icon(key)
                if icon:
                    key_base_id = icon.split("_")[0]
                    if key_base_id in seen_base_id:
                        continue
                    seen_base_id.add(key_base_id)
            self.coabs[key] = coab
            if key != self.coab_qual:
                self.coab_list.append(key)
                max_coabs -= 1
            if coab["ex"] and (coab["category"] not in ex_ab or coab["ex"][0][1] > ex_ab[coab["category"]][0][1]):
                ex_ab[coab["category"]] = coab["ex"]
            for chain in coab["chain"]:
                full_ab.append(tuple(chain))
                if key != self.coab_qual:
                    if chain[0] == "ctime":
                        self._chain_ctime += chain[1]
                        self._ctime_coabs.append((chain[1], key, coab))
                    if chain[0] in ("hp", "rcv"):
                        self._healing_coabs.append((key, coab))
                    if chain[0].endswith("regen") or chain[0].endswith("heal"):
                        self._regen_coabs.append((key, coab))
                    if chain[0] == "bt":
                        self._bufftime_coabs.append((key, coab))
            if max_coabs == 0:
                break
        for ex_list in ex_ab.values():
            full_ab.extend(map(tuple, ex_list))
        if self.wt == "axe":
            full_ab.append(("cc", 0.04))
        else:
            full_ab.append(("cc", 0.02))
        self.coab_list = sorted(self.coab_list)
        return full_ab

    def fort_mod(self, key):
        if CharaBase.FORT_KEY == None:
            return 1
        fort_conf = CharaBase.FORT[CharaBase.FORT_KEY]
        return 1 + (fort_conf["ele"][key][self.ele] + fort_conf["wep"][key][self.wt]) / 100

    @property
    def att(self):
        return super().att * self.fort_mod("att")

    @property
    def hp(self):
        return super().att * self.fort_mod("hp")

    @property
    def ele(self):
        return self.conf.ele

    @property
    def wt(self):
        return self.conf.wt


class EquipBase(SlotBase):
    def __init__(self, conf, c, qual=None):
        super().__init__(conf, qual)
        self.c = c

    @property
    def on_ele(self):
        try:
            return self.conf["ele"] == self.c.ele
        except:
            return False

    @property
    def att(self):
        return super().att * (1 + 0.5 * int(self.on_ele))

    @property
    def hp(self):
        return super().hp * (1 + 0.5 * int(self.on_ele))


class DragonBase(EquipBase):
    AUGMENTS = 50
    FAFNIR = 0.115
    DEFAULT_DCONF = Conf(
        {
            "dacl": "ds1,x=3", # the default dacl
            "duration": 10.0,  # 10s dragon time
            "dracolith": 0.70,  # base dragon damage
            "exhilaration": 0,  # psiren aura
            "default_ds_x": 0,
            "default_x_loop": 0,
            "dshift.startup": 1.0,
            "dshift.recovery": 0.63333,
            "dshift.attr": [{"dmg": 2.0}],
            "dodge.startup": 0.0,
            "dodge.recovery": 0.66667,
            "dodge.interrupt": {"s": 0.0},
            "dodge.cancel": {"s": 0.0},
            "dend.startup": 0.0,
            "dend.recovery": 0.0,
            "allow_end": 3.0,  # time before force end is allowed, not including the time needed for skill
            "allow_end_step": 2.0,  # for each shift, add this amount of time to allow_end
        }
    )

    def __init__(self, conf, c, qual=None):
        super().__init__(conf.d, c, qual)
        self.dform = conf

    def oninit(self, adv):
        if adv.conf["dragonform"]:
            name = self.c.name
            self.dform = Conf(adv.conf["dragonform"])
        else:
            name = self.name
        self.dform.update(DragonBase.DEFAULT_DCONF, rebase=True)

        if self.c.conf["utp"]:
            from core.dragonform import DragonFormUTP

            drgclass = DragonFormUTP
        else:
            from core.dragonform import DragonForm

            drgclass = DragonForm

        adv.dragonform = drgclass(name, self.dform, adv, self)
        self.adv = adv

    @property
    def att(self):
        return super().att * (1 + DragonBase.FAFNIR)

    @property
    def hp(self):
        return super().hp * (1 + DragonBase.FAFNIR)

    @property
    def ele(self):
        return self.conf.ele

    @property
    def ab(self):
        return super().ab if self.on_ele else []


from core.modifier import EffectBuff, SelfAffliction, Selfbuff, SingleActionBuff
from core.timeline import Listener, Timer, now, Event
from core.log import log


class Gala_Reborn(DragonBase):
    def oninit(self, adv, buff_name, buff_ele):
        super().oninit(adv)
        self.dp_count = 0
        Event("dp").listener(self.dp_reborn_buff)
        self.reborn_buff = adv.Selfbuff(buff_name, 0.3, 45, buff_ele, "ele").no_bufftime()
        setattr(adv, buff_name, adv.Selfbuff(buff_name, 0.3, 45, buff_ele, "ele").no_bufftime())

    def dp_reborn_buff(self, e):
        self.dp_count += e.value
        if self.dp_count >= 100.0:
            self.reborn_buff.on()
            self.dp_count -= 100.0


### FLAME DRAGONS ###
class Gala_Mars(DragonBase):
    def shift_end_proc(self):
        self.adv.charge_p("shift_end", 100)


class Gozu_Tenno(DragonBase):
    def oninit(self, adv):
        from core.advbase import Repeat, Fs

        super().oninit(adv)
        adv.gozu_tenno_buff = adv.Selfbuff("gozu_tenno_buff", 0.3, 30, "flame", "ele").no_bufftime()

        def fs_end(e):
            fs_action = adv.action.getdoing()
            if not isinstance(fs_action, Fs):
                fs_action = adv.action.getprev()
            if isinstance(fs_action, Repeat):
                fs_action = fs_action.parent
            fs_elapsed = now() - fs_action.startup_start - fs_action.last_buffer + 0.0001  # float shenanigans
            if fs_elapsed >= 3.0:
                adv.gozu_tenno_buff.on(30)

        Event("fs_end").listener(fs_end, order=0)
        Event("repeat").listener(fs_end, order=0)


class Gala_Reborn_Agni(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gagni_buff", "flame")


### FLAME DRAGONS ###

### WATER DRAGONS ###
class Nimis(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)

        def add_gauge_and_time(t):
            adv.dragonform.charge_dprep(20)
            adv.dragonform.extend_shift_time(5, percent=False)

        Event("ds").listener(add_gauge_and_time)


class Gala_Reborn_Poseidon(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gposeidon_buff", "water")


class Gabriel(DragonBase):
    def gab_buff_on(self, e):
        return self.gabriel_favor.on()

    def oninit(self, adv):
        super().oninit(adv)
        self.gabriel_favor = Selfbuff("gabriel_favor", 0.1, -1, "att", "buff")

        adv.heal_event.listener(self.gab_buff_on)


### WATER DRAGONS ###

### WIND DRAGONS ###
class AC011_Garland(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        if adv.condition("maintain shield"):
            Timer(lambda _: adv.Modifier("d_1_dauntless", "att", "passive", 0.30).on(), 15).on()


class Summer_Konohana_Sakuya(DragonBase):
    FLOWER_BUFFS = {
        1: (0.40, -1, "att", "buff"),
        2: (0.20, -1, "defense", "buff"),
        3: (0.50, -1, "s", "buff"),
        4: (0.05, -1, "res", "water"),
        6: (0.20, -1, "regen", "buff"),
    }
    FLOWER_BUFFS_NIHIL = {
        4: (0.05, -1, "res", "water"),
        6: (0.20, -1, "regen", "buff"),
    }

    def add_flower(self, t=None):
        if self.adv.summer_sakuya_flowers >= 6:
            return
        self.adv.summer_sakuya_flowers += 1
        try:
            self.adv.Selfbuff(
                f"d_sakuya_flower_{self.adv.summer_sakuya_flowers}",
                *self.flower_buffs[self.adv.summer_sakuya_flowers],
            ).on()
        except KeyError:
            pass

    def oninit(self, adv):
        super().oninit(adv)
        adv.summer_sakuya_flowers = 0
        self.flower_buffs = Summer_Konohana_Sakuya.FLOWER_BUFFS
        if adv.nihilism:
            self.flower_buffs = Summer_Konohana_Sakuya.FLOWER_BUFFS_NIHIL

        self.add_flower()
        Timer(self.add_flower, 60, True).on()
        Event("ds").listener(self.add_flower)


class Gala_Reborn_Zephyr(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gzephyr_buff", "wind")


class Menoetius(DragonBase):
    def l_selfaff_proc(self, e):
        if self.adv.is_set_cd("menoetius_aura", 20):
            self.deranged_thrill.on()
            # confirm which mod is used
            # adv.dmg_make("#menoetius_aura", 27.53)
            self.adv.dmg_make("#menoetius_aura", 24.57)

    def oninit(self, adv):
        super().oninit(adv)
        self.deranged_thrill = Selfbuff("deranged_thrill", 0.25, 45, "att", "passive")
        Event("selfaff").listener(self.l_selfaff_proc)


class Rose_Queen(DragonBase):
    def ds1_proc(self, e):
        log("ds_proc_slayer", "rose_queen")
        self.slayed_event()

    def oninit(self, adv):
        super().oninit(adv)

        self.slayed_event = Event("slayed")
        self.slayed_event.count = 25
        self.slayed_event.name = "dx"


class Gala_Beast_Volk(DragonBase):
    def d_moon_repeat(self, t):
        self.adv.moonlit_rage = min(10, self.adv.moonlit_rage + 1)
        self.adv.dmg_make("dmoon", 2.58)
        self.adv.add_hp(10)

    def ds1_proc(self, e):
        log("ds1_proc", e.name, e.group)
        if e.group == 0:
            self.blood_moon_timer.on()
            self.adv.charge_p("ds1", 100, target="ds1", dragon_sp=True)
        else:
            self.blood_moon_timer.off()
            self.adv.blood_moon = 0
            self.adv.moonlit_rage = 0
            self.adv.a_s_dict["ds1"].set_enabled(False)

    def shift_end_proc(self):
        SelfAffliction("gala_beast_volk_poison", -10, [12, 2.9], affname="poison").on()

    def oninit(self, adv):
        super().oninit(adv)
        self.adv.blood_moon = 0
        self.adv.moonlit_rage = 0
        self.blood_moon_timer = Timer(self.d_moon_repeat, 3.5, True)


### WIND DRAGONS ###

### LIGHT DRAGONS ###
class Gala_Thor(DragonBase):
    def chariot_energy(self, t):
        self.adv.energy.add(1)

    def shift_end_proc(self):
        self.adv.energy.add(5, team=True)

    def oninit(self, adv):
        super().oninit(adv)
        Timer(self.chariot_energy, 5, True).on()


class Lumiere_Pandora(DragonBase):
    def add_joyful_radiance(self, e):
        if self.adv.joyful_radiance == 0:
            self.joyful_radiance_buff.on()
        self.adv.joyful_radiance = min(4, self.adv.joyful_radiance + 1)
        self.joyful_radiance_buff.value(self.adv.joyful_radiance * 0.2)

    def expire_joyful_radiance(self, t):
        self.adv.joyful_radiance = max(0, self.adv.joyful_radiance - 1)
        if self.adv.joyful_radiance == 0:
            self.joyful_radiance_buff.off()
        else:
            self.joyful_radiance_buff.value(self.adv.joyful_radiance * 0.2)

    def oninit(self, adv):
        super().oninit(adv)
        if not adv.nihilism:
            self.joyful_radiance_buff = adv.Selfbuff("joyful_radiance", 0.8, -1, "att", "passive").on()
            adv.joyful_radiance = 4

            Event("buffskills").listener(self.add_joyful_radiance)

            Timer(self.expire_joyful_radiance, 20, True).on()


class Gala_Reborn_Jeanne(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gjeanne_buff", "light")


### LIGHT DRAGONS ###

### SHADOW DRAGONS ###
class Gala_Cat_Sith(DragonBase):
    MAX_TRICKERY = 14
    THRESHOLD = 25

    def add_trickery(self, t):
        if not self.adv.nihilism:
            self.adv.trickery = min(self.adv.trickery + t, Gala_Cat_Sith.MAX_TRICKERY)
            log("trickery", f"+{t}", self.adv.trickery, self.adv.hits)

    def check_trickery(self, e=None):
        if self.adv.trickery > 0 and not self.trickery_buff.get():
            self.adv.trickery -= 1
            log("trickery", "-1", self.adv.trickery)
            self.trickery_buff.on()

    def combo_trickery(self, e):
        n_thit = e.hits // Gala_Cat_Sith.THRESHOLD
        if n_thit > self.thit:
            self.add_trickery(1)
        self.thit = n_thit
        self.check_trickery()

    def shift_end_proc(self):
        self.add_trickery(8)

    def oninit(self, adv):
        super().oninit(adv)
        adv.trickery = Gala_Cat_Sith.MAX_TRICKERY
        if not adv.nihilism:
            self.thit = 0
            self.trickery_buff = SingleActionBuff("d_trickery_buff", 1.80, 1, "s", "buff").on()
            self.l_hit = Event("hit").listener(self.combo_trickery)


class Fatalis(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        adv.dragonform.set_disabled("Fatalis")

    @property
    def ab(self):
        return super().ab if self.on_ele else [["a", 0.5]]


class Ramiel(DragonBase):
    def ds1_proc(self, e):
        self.sp_regen_buff.on()

    def oninit(self, adv):
        super().oninit(adv)
        self.sp_regen_timer = Timer(lambda _: adv.charge_p("ds_sp", 0.0075, target=["s1", "s2"]), 0.99, True)
        self.sp_regen_buff = EffectBuff("ds_sp", 90, lambda: self.sp_regen_timer.on(), lambda: self.sp_regen_timer.off())


class Gold_Fafnir(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        # disabled for convienance
        adv.dragonform.set_disabled("Gold_Fafnir")


class Arsene(DragonBase):
    @property
    def ab(self):
        return super().ab if self.on_ele else [["s", 0.9]]


class Gala_Reborn_Nidhogg(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gnidhogg_buff", "shadow")


### SHADOW DRAGONS ###


class WeaponBase(EquipBase):
    def __init__(self, conf, c, series):
        super().__init__(conf.w, c, f"{c.wt}-{c.ele}-{series}")
        self.s3_conf = {sn: sconf for sn, sconf in conf.find(r"s3.*")}
        self.series = series

    @property
    def s3(self):
        if self.on_ele or self.ele == "any":
            return self.s3_conf

    @property
    def ele(self):
        return self.conf.ele


APGroup = namedtuple("APGroup", ["value", "att", "restrict", "condition", "union", "qual"])


class AmuletPicker:
    UNION_THRESHOLD = {1: 4, 2: 4, 3: 4, 4: 3, 5: 2, 6: 2, 11: 2}

    def __init__(self):
        self._grouped = {1: {}, 2: {}, 3: {}}
        self._grouped_lookup = {}
        special_counter = 0
        for qual, wp in wyrmprints.items():
            ab_length = len(wp["a"])
            if ab_length == 1:
                wpa_lst = wp["a"][0]
                wpa = wpa_lst[0]
                wpv = wpa_lst[1]
                try:
                    parts = wpa_lst[2].split("_")
                    wpc = tuple(c for c in parts if c not in ELEMENTS and c not in WEAPON_TYPES)
                    wpr = tuple(c for c in parts if c in ELEMENTS or c in WEAPON_TYPES)
                except (AttributeError, IndexError):
                    wpc = tuple()
                    wpr = tuple()
            else:
                wpv = 0
                if ab_length > 1:
                    wpa = ("special", special_counter)
                    special_counter += 1
                else:
                    wpa = (None,)
                wpc = None
                wpr = None

            grouped_value = APGroup(
                value=wpv,
                att=wp["att"],
                restrict=wpr,
                condition=wpc,
                union=wp["union"],
                qual=qual,
            )
            group_key = wp["rarity"]
            self._grouped_lookup[qual] = (group_key, wpa, grouped_value)
            try:
                from bisect import bisect

                idx = bisect(self._grouped[group_key][wpa], grouped_value)
                self._grouped[group_key][wpa].insert(idx, grouped_value)
            except KeyError:
                self._grouped[group_key][wpa] = [grouped_value]

    def get_group(self, qual):
        rare, gkey, gval = self._grouped_lookup[qual]
        return self._grouped[rare][gkey], gval

    @staticmethod
    def find_next_matching(bis_i, group, gval, c, retain_union):
        # for reasons unbeknown to me this comment has to exist in order for Liber Grimoris to sort over Mana Fount
        # perhaps it is some kind of seriously cursed interpreter level short circuiting
        # bool(group[bis_i].restrict) and not (c.wt in group[bis_i].restrict or c.ele in group[bis_i].restrict
        while bis_i > 0 and (
            (bool(group[bis_i].restrict) and not (c.wt in group[bis_i].restrict or c.ele in group[bis_i].restrict))
            or (group[bis_i].condition and group[bis_i].condition and gval.condition != group[bis_i].condition)
            or (gval.union in retain_union and gval.union != group[bis_i].union)
        ):
            bis_i -= 1
        return bis_i

    def pick(self, amulets, c):
        union_threshold = AmuletPicker.UNION_THRESHOLD.copy()
        for a in amulets:
            for ab in a.ab:
                if ab[0] == "psalm":
                    _, union, min_count, extra_level = ab
                    union_threshold[union] = max(min_count, union_threshold[union] - extra_level)

        retain_union = {}
        for u, thresh in union_threshold.items():
            u_sum = sum(a.union == u for a in amulets)
            if u_sum >= thresh:
                retain_union[u] = u_sum

        new_amulet_quals = set()
        for a_i, a in enumerate(amulets):
            # always keep psalm print
            if any((ab[0] == "psalm" for ab in a.ab)):
                new_amulet_quals.add(a.qual)
                continue
            group, gval = self.get_group(a.qual)
            if len(group) == 1:
                new_amulet_quals.add(a.qual)
                continue
            bis_i = len(group) - 1
            bis_i = self.find_next_matching(bis_i, group, gval, c, retain_union)
            while group[bis_i].qual in new_amulet_quals:
                bis_i -= 1
                bis_i = self.find_next_matching(bis_i, group, gval, c, retain_union)
            bis_qual = group[bis_i].qual
            amulets[a_i] = AmuletBase(Conf(wyrmprints[bis_qual]), c, bis_qual)
            new_amulet_quals.add(bis_qual)

        return amulets


class AmuletStack:
    AB_LIMITS = {
        "a": 0.20,
        "s": 0.40,
        "cc": 0.15,
        "cd": 0.25,
        "fs": 0.50,
        "bt": 0.30,
        "dbt": 0.20,
        "sp": 0.15,
        "spf": 0.15,
        "bk": 0.30,
        "od": 0.15,
        "lo_att": 0.60,
        "lo_defense": 1.0,
        "ro_att": 0.10,
        "bc_att": 0.15,
        "bc_cd": 0.15,
        "bc_energy": 1,
        "bc_regen": 3,
        "prep": 100,
        "eprep": 5,
        "dc": 3,
        "dcs": 3,
        "dcd": 3,
        "da": 0.18,
        "dh": 0.15,
        "dt": 0.20,
        "spu": 0.08,
        "au": 0.08,
        "affself_poison_crit_damage": 0.3,
        "k_burn": 0.30,
        "k_poison": 0.30,
        "k_paralysis": 0.25,
        "k_frostbite": 0.25,
        "k_stun": 0.25,
        "k_sleep": 0.25,
        "k_shadowblight": 0.25,
        "k_stormlash": 0.25,
        "k_flashburn": 0.25,
        "bleed": 0.15,
        "rcv": 0.20,
        "hp": 0.15,
    }
    # actually depends on weapons kms
    RARITY_LIMITS = {1: 3, 2: 2, 3: 2}
    PICKER = AmuletPicker()

    def __init__(self, confs, c, quals):
        limits = AmuletStack.RARITY_LIMITS.copy()
        self.an = []
        icon_ids = set()
        for conf, qual in zip(confs, quals):
            if limits[conf["rarity"]] == 0:
                continue
            limits[conf["rarity"]] -= 1
            amulet = AmuletBase(conf, c, qual)
            if amulet.icon not in icon_ids:
                self.an.append(amulet)
                icon_ids.add(amulet.icon)
        # if any(limits.values()):
        #     raise ValueError("Unfilled wyrmprint slot")
        self.an = AmuletStack.PICKER.pick(self.an, c)
        self.an.sort(key=lambda a: (a.rarity, a.name))
        self.c = c

    def __str__(self):
        return "+".join(map(str, self.an))

    @property
    def att(self):
        return sum(a.att for a in self.an)

    @property
    def hp(self):
        return sum(a.hp for a in self.an)

    @property
    def qual_lst(self):
        return [a.qual for a in self.an]

    @property
    def name_lst(self):
        return (a.name for a in self.an)

    def name_icons(self):
        return [a.name_icon() for a in self.an]

    @staticmethod
    def sort_ab(a):
        if a[1] < 0:
            return -10000
        try:
            if "hp" not in a[2]:
                return -1 * a[1]
        except (TypeError, IndexError):
            return -100 * a[1]
        return a[1]

    @property
    def ab(self):
        merged_ab = []

        limits = AmuletStack.AB_LIMITS.copy()
        sorted_ab = defaultdict(list)
        psalm_ab = []
        for a in chain(*(a.ab for a in self.an)):
            if a[0] in limits:
                sorted_ab[a[0]].append(a)
            elif a[0] == "psalm":
                psalm_ab.append(a)
            else:
                merged_ab.append(a)

        base_union_level = defaultdict(lambda: defaultdict(lambda: 0))
        limit_union_level = defaultdict(lambda: 3)
        for _, union, min_count, extra_level in psalm_ab:
            if limit_union_level[union] > 0:
                base_union_level[union][min_count] += extra_level
            limit_union_level[union] -= 1

        for cat, lst in sorted_ab.items():
            for a in sorted(lst, key=AmuletStack.sort_ab):
                delta = min(limits[cat], a[1])
                limits[cat] -= delta
                merged_ab.append((cat, delta, *a[2:]))
                if limits[cat] == 0:
                    break

        union_level = defaultdict(lambda: 0)
        for a in self.an:
            if a.union:
                union_level[a.union] += 1
                union_level[a.union] += base_union_level[a.union][union_level[a.union]]

        merged_ab.extend((("union", u, l) for u, l in union_level.items()))

        return merged_ab


class AmuletBase(EquipBase):
    KIND = "a"
    AUGMENTS = 50

    def __init__(self, conf, c, qual=None):
        super().__init__(conf, c, qual)
        # form C
        if self.rarity == 3:
            self.att_augment -= 10
            self.hp_augment -= 10

    @property
    def union(self):
        return self.conf.union

    @property
    def rarity(self):
        return self.conf.rarity


class Slots:
    DRAGON_DICTS = subclass_dict(DragonBase)

    DEFAULT_DRAGON = {
        "flame": "Gala_Agni",
        "water": "Gala_Reborn_Poseidon",
        "wind": "Gala_Beast_Volk",
        "light": "Gala_Reborn_Jeanne",
        "shadow": "Gala_Cat_Sith",
    }

    DEFAULT_WYRMPRINT = [
        "Valiant_Crown",
        "Gentle_Winds",
        "The_Chocolatiers",
        "Beautiful_Nothingness",
        "Dueling_Dancers",
    ]

    DEFAULT_WEAPON = "agito"

    def __init__(self, name, conf, sim_afflict=None, flask_env=False):
        self.c = CharaBase(conf, name)
        self.sim_afflict = sim_afflict
        self.flask_env = flask_env
        self.d = None
        self.w = None
        self.a = None
        self.abilities = {}

    def __str__(self):
        return ",".join(
            [
                self.c.name,
                self.c.ele,
                self.c.wt,
                str(round(self.att)),
                self.d.name,
                self.w.name,
                *self.a.name_lst,
            ]
        )

    @staticmethod
    def get_with_alias(source, k):
        try:
            return Conf(source[k]), k
        except KeyError:
            k = alias[k.lower()]
            return Conf(source[k]), k

    def set_d(self, key=None):
        if not key:
            key = Slots.DEFAULT_DRAGON[self.c.ele]
        try:
            conf, key = Slots.get_with_alias(dragons[self.c.ele], key)
        except KeyError:
            for ele in ELEMENTS:
                if ele == self.c.ele:
                    continue
                try:
                    conf, key = Slots.get_with_alias(dragons[ele], key)
                    break
                except KeyError:
                    pass
        try:
            self.d = Slots.DRAGON_DICTS[key](conf, self.c, key)
        except KeyError:
            self.d = DragonBase(conf, self.c, key)

    def set_w(self, key=None):
        try:
            conf = Conf(weapons[self.c.wt][self.c.ele][key])
        except KeyError:
            try:
                conf = Conf(weapons[self.c.wt]["any"][key])
            except KeyError:
                conf = Conf(weapons[self.c.wt][self.c.ele][Slots.DEFAULT_WEAPON])
                key = Slots.DEFAULT_WEAPON
        self.w = WeaponBase(conf, self.c, key)

    def set_a(self, keys=None):
        if keys is None or len(keys) < 5:
            keys = list(set(Slots.DEFAULT_WYRMPRINT))
        else:
            keys = list(set(keys))
        # if len(keys) < 5:
        #     raise ValueError('Less than 5 wyrmprints equipped')
        confs = [Slots.get_with_alias(wyrmprints, k)[0] for k in keys]
        self.a = AmuletStack(confs, self.c, keys)

    def set_slots(self, confslots):
        for t in ("d", "w", "a"):
            getattr(self, f"set_{t}")(confslots[t])

    @property
    def att(self):
        return self.c.att + self.d.att + self.w.att + self.a.att

    @property
    def hp(self):
        return self.c.hp + self.d.hp + self.w.hp + self.a.hp

    def oninit(self, adv=None):
        for kind, slot in (("c", self.c), ("d", self.d), ("a", self.a), ("w", self.w)):
            for aidx, ab in enumerate(slot.ab):
                name = ab[0]
                if "_" in name:
                    acat = name.split("_")[0]
                else:
                    acat = name
                try:
                    self.abilities[f"ab_{kind}{aidx}"] = ability_dict[acat](*ab)
                except:
                    pass

        for key, ab in self.abilities.items():
            ab.oninit(adv, key)
