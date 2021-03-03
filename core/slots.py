from itertools import chain, islice
from collections import defaultdict
from collections import namedtuple
import html

from conf import (
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

    @property
    def att(self):
        return self.conf.att + self.AUGMENTS

    @property
    def hp(self):
        return self.conf.hp + self.AUGMENTS

    @property
    def ab(self):
        if self.conf["a"]:
            return self.conf.a
        return []

    def oninit(self, adv):
        pass


class CharaBase(SlotBase):
    AUGMENTS = 100
    FAC_ELEMENT_ATT = {
        "all": {"altar": 0.26, "slime": 0.04},
        "flame": {"tree": 0.31, "arctos": 0.085},
        "water": {"tree": 0.26, "yuletree": 0.085, "dragonata": 0.085},
        "wind": {"tree": 0.26, "shrine": 0.085},
        "light": {"tree": 0.26, "retreat": 0.085, "circus": 0.085},
        "shadow": {"tree": 0.31, "library": 0.085},
    }
    FAC_ELEMENT_HP = FAC_ELEMENT_ATT.copy()
    FAC_ELEMENT_HP["flame"]["arctos"] = 0.095
    FAC_ELEMENT_HP["water"]["yuletree"] = 0.095
    FAC_ELEMENT_HP["water"]["dragonata"] = 0.095
    FAC_ELEMENT_HP["wind"]["shrine"] = 0.095
    FAC_ELEMENT_HP["light"]["retreat"] = 0.095
    FAC_ELEMENT_HP["light"]["circus"] = 0.095
    FAC_ELEMENT_HP["shadow"]["library"] = 0.095

    FAC_WEAPON_ATT = {
        "all": {"dojo": 0.33, "weap": 0.225},
        "dagger": 0.11,
        "bow": 0.11,
        "blade": 0.06,
        "wand": 0.06,
        "sword": 0.05,
        "lance": 0.05,
        "staff": 0.05,
        "axe": 0.05,
        "gun": -0.1,  # opera (0.05) + fount (0.05) - diff in weap (0.225 - 0.205 = 0.2)
    }
    FAC_WEAPON_HP = FAC_WEAPON_ATT.copy()

    NON_UNIQUE_COABS = ("Sword", "Blade", "Dagger", "Bow", "Wand", "Axe2", "Dagger2")
    MAX_COAB = 3  # max allowed coab, excluding self

    def __init__(self, conf, qual=None):
        super().__init__(conf, qual)
        self.coabs = {}
        self.coab_list = []
        self.coab_qual = None
        self.valid_coabs = elecoabs[self.ele]
        if self.conf["ex"]:
            self.coabs[self.qual] = self.conf["ex"]
            self.coab_qual = self.qual
        else:
            try:
                self.coabs[self.qual] = self.valid_coabs[self.qual]
                self.coab_qual = self.qual
            except KeyError:
                try:
                    wt = self.wt
                    upper_wt = wt[0].upper() + wt[1:].lower()
                    self.coabs[upper_wt] = self.valid_coabs[upper_wt]
                    self.coab_qual = upper_wt
                except KeyError:
                    pass

    @property
    def ab(self):
        full_ab = list(super().ab)
        ex_set = set()
        max_coabs = CharaBase.MAX_COAB
        coabs = list(self.coabs.items())
        self.coabs = {}
        self.coab_list = []
        for key, coab in coabs:
            # alt check
            if key not in CharaBase.NON_UNIQUE_COABS:
                key_base_id = get_icon(key).split("_")
                self_base_id = self.icon.split("_")
                if key_base_id[0] == self_base_id[0] and key_base_id[1] != self_base_id[1]:
                    continue
            self.coabs[key] = coab
            if key != self.coab_qual:
                self.coab_list.append(key)
                max_coabs -= 1
            chain, ex = coab
            if ex:
                ex_set.add(("ex", ex))
            if chain:
                full_ab.append(tuple(chain))
            if max_coabs == 0:
                break
        # speshul clause maybe fix later
        if ("ex", "sophie") in ex_set and ("ex", "peony") in ex_set:
            ex_set.remove(("ex", "sophie"))
        full_ab.extend(ex_set)
        if self.wt == "axe":
            full_ab.append(("cc", 0.04))
        else:
            full_ab.append(("cc", 0.02))
        return full_ab

    @property
    def att(self):
        FE = CharaBase.FAC_ELEMENT_ATT
        FW = CharaBase.FAC_WEAPON_ATT
        halidom_mods = 1 + sum(FE["all"].values()) + sum(FE[self.ele].values()) + sum(FW["all"].values()) + FW[self.wt]
        return super().att * halidom_mods

    @property
    def hp(self):
        FE = CharaBase.FAC_ELEMENT_HP
        FW = CharaBase.FAC_WEAPON_HP
        halidom_mods = 1 + sum(FE["all"].values()) + sum(FE[self.ele].values()) + sum(FW["all"].values()) + FW[self.wt]
        return super().hp * halidom_mods

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
            "duration": 10,  # 10s dragon time
            "dracolith": 0.70,  # base dragon damage
            "exhilaration": 0,  # psiren aura
            "gauge_val": 100,  # gauge regen value
            "latency": 0,  # amount of delay for cancel
            "act": "c3-s",
            "dshift.startup": 1.0,
            "dshift.recovery": 0.63333,
            "dshift.attr": [{"dmg": 2.0}],
            "dodge.startup": 0.0,
            "dodge.recovery": 0.66667,
            "end.startup": 0,
            "end.recovery": 0,
            "allow_end": 3.0,  # time before force end is allowed, not including the time needed for skill
            "allow_end_step": 2.0,  # for each shift, add this amount of time to allow_end
        }
    )

    def __init__(self, conf, c, qual=None):
        super().__init__(conf.d, c, qual)
        self.dragonform = conf

    def oninit(self, adv):
        from core.dragonform import DragonForm

        for dn, dconf in self.dragonform.items():
            if isinstance(dconf, dict):
                adv.hitattr_check(dn, dconf)
        if adv.conf["dragonform"]:
            name = self.c.name
            self.dragonform.update(adv.conf["dragonform"])
        else:
            name = self.name
        self.dragonform.update(DragonBase.DEFAULT_DCONF, rebase=True)
        adv.dragonform = DragonForm(name, self.dragonform, adv)

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


from core.modifier import EffectBuff, Selfbuff, SingleActionBuff
from core.timeline import Timer, now, Event
from core.log import log


class Gala_Reborn(DragonBase):
    def oninit(self, adv, buff_name, buff_ele):
        super().oninit(adv)
        charge_gauge_o = adv.dragonform.charge_gauge
        self.agauge = 0
        self.acount = 0
        setattr(adv, buff_name, adv.Selfbuff(buff_name, 0.3, 45, buff_ele, "ele").no_bufftime())

        def charge_gauge(value, **kwargs):
            delta = charge_gauge_o(value, **kwargs)
            self.agauge += delta
            n_acount = self.agauge // 100
            if n_acount > self.acount:
                self.acount = n_acount
                getattr(adv, buff_name).on()

        adv.dragonform.charge_gauge = charge_gauge


### FLAME DRAGONS ###
class Gala_Mars(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)

        def shift_end_prep(e):
            adv.charge_p("shift_end", 100)

        Event("dragon_end").listener(shift_end_prep)


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
            fs_elapsed = now() - fs_action.startup_start
            if fs_elapsed >= 3.0:
                adv.gozu_tenno_buff.on(30)

        Event("fs_end").listener(fs_end, order=0)
        Event("repeat").listener(fs_end, order=0)


### FLAME DRAGONS ###

### WATER DRAGONS ###
class Gaibhne_and_Creidhne(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        charge_timer = Timer(lambda _: adv.charge_p("ds", 0.091, no_autocharge=True), 0.9, True)
        ds_buff = EffectBuff(
            "ds_sp_regen_zone",
            10,
            lambda: charge_timer.on(),
            lambda: charge_timer.off(),
        )
        Event("ds").listener(lambda _: ds_buff.on())


class Nimis(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)

        def add_gauge_and_time(t):
            adv.dragonform.charge_gauge(200, dhaste=False)
            adv.dragonform.set_shift_end(5, percent=False)

        Event("ds").listener(add_gauge_and_time)


class Styx(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        adv.styx_spirit = 0
        adv.csd_buff = SingleActionBuff("d_compounding_sd", 0.0, -1, "s", "buff")

        def add_csd(e):
            if not adv.csd_buff.get():
                adv.csd_buff.set(min(2.00, adv.csd_buff.get() + 0.50))
                adv.csd_buff.on()
            else:
                adv.csd_buff.value(min(2.00, adv.csd_buff.get() + 0.50))

        csd_timer = Timer(add_csd, 15, True).on()

        def add_spirit(e):
            if e.index == 3:
                adv.styx_spirit = min(3, adv.styx_spirit + 1)
                log("dx_spirit", adv.styx_spirit)

        Event("dx").listener(add_spirit)

        def reset_spirit(e):
            adv.styx_spirit = 0

        Event("ds").listener(reset_spirit)
        Event("dragon_end").listener(reset_spirit)


class Gala_Reborn_Poseidon(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gposeidon_buff", "water")


class Gabriel(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        self.gabriel_favor = Selfbuff("gabriel_favor", 0.1, -1, "att", "buff")

        def gab_buff_on(_):
            return self.gabriel_favor.on()

        adv.heal_event.listener(gab_buff_on)


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

    def oninit(self, adv):
        super().oninit(adv)
        adv.summer_sakuya_flowers = 0

        def add_flower(t=None):
            if adv.summer_sakuya_flowers >= 6:
                return
            adv.summer_sakuya_flowers += 1
            try:
                adv.Selfbuff(
                    f"d_sakuya_flower_{adv.summer_sakuya_flowers}",
                    *self.FLOWER_BUFFS[adv.summer_sakuya_flowers],
                ).on()
            except KeyError:
                pass

        add_flower()
        Timer(add_flower, 60, True).on()
        Event("ds").listener(add_flower)


class Gala_Reborn_Zephyr(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gzephyr_buff", "wind")


class Menoetius(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        self.deranged_thrill = Selfbuff("deranged_thrill", 0.25, 45, "att", "passive")
        self.is_cd = False

        def cd_end(e):
            self.is_cd = False

        def l_selfaff_proc(e):
            if not self.is_cd:
                self.deranged_thrill.on()
                # confirm which mod is used
                # adv.dmg_make("#menoetius_aura", 27.53)
                adv.dmg_make("#menoetius_aura", 24.57)
                self.is_cd = True
                Timer(cd_end, 20).on()

        Event("selfaff").listener(l_selfaff_proc)


### WIND DRAGONS ###

### LIGHT DRAGONS ###
class Gala_Thor(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)

        def chariot_energy(t):
            adv.energy.add(1)

        Timer(chariot_energy, 5, True).on()

        def shift_end_energy(e):
            adv.energy.add(5, team=True)

        Event("dragon_end").listener(shift_end_energy)


class Lumiere_Pandora(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        joyful_radiance_buff = adv.Selfbuff("joyful_radiance", 0.8, -1, "att", "passive").on()
        adv.joyful_radiance = 4

        def add_joyful_radiance(e):
            if adv.joyful_radiance == 0:
                joyful_radiance_buff.on()
            adv.joyful_radiance = min(4, adv.joyful_radiance + 1)
            joyful_radiance_buff.value(adv.joyful_radiance * 0.2)

        Event("buffskills").listener(add_joyful_radiance)

        def expire_joyful_radiance(t):
            adv.joyful_radiance = max(0, adv.joyful_radiance - 1)
            if adv.joyful_radiance == 0:
                joyful_radiance_buff.off()
            else:
                joyful_radiance_buff.value(adv.joyful_radiance * 0.2)

        Timer(expire_joyful_radiance, 20, True).on()


class Gala_Reborn_Jeanne(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gjeanne_buff", "light")


### LIGHT DRAGONS ###

### SHADOW DRAGONS ###
class Gala_Cat_Sith(DragonBase):
    MAX_TRICKERY = 14

    def oninit(self, adv):
        super().oninit(adv)
        adv.trickery = Gala_Cat_Sith.MAX_TRICKERY
        threshold = 25
        self.trickery_buff = SingleActionBuff("d_trickery_buff", 1.80, 1, "s", "buff").on()

        def add_trickery(t):
            adv.trickery = min(adv.trickery + t, Gala_Cat_Sith.MAX_TRICKERY)
            log("debug", "trickery", f"+{t}", adv.trickery, adv.hits)

        def check_trickery(e=None):
            if adv.trickery > 0 and not self.trickery_buff.get():
                adv.trickery -= 1
                log("debug", "trickery", "-1", adv.trickery)
                self.trickery_buff.on()

        def shift_end_trickery(e=None):
            if not adv.dragonform.is_dragondrive:
                add_trickery(8)

        Event("dragon_end").listener(shift_end_trickery)
        if adv.condition("always connect hits"):
            add_combo_o = adv.add_combo
            self.thit = 0

            def add_combo(name="#"):
                result = add_combo_o(name)
                n_thit = adv.hits // threshold
                if n_thit > self.thit:
                    add_trickery(1)
                self.thit = n_thit
                check_trickery()
                return result

            adv.add_combo = add_combo


class Fatalis(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        adv.dragonform.disabled = True

    @property
    def ab(self):
        return super().ab if self.on_ele else [["a", 0.5]]


class Nyarlathotep(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)

        def bloody_tongue(t=None):
            adv.Buff("bloody_tongue", 0.30, 20).on()

        bloody_tongue(0)
        buff_rate = 90
        if adv.condition(f"hp=30% every {buff_rate}s"):
            buff_times = int(adv.duration // buff_rate)
            for i in range(1, buff_times):
                adv.Timer(bloody_tongue).on(buff_rate * i)


class Ramiel(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        sp_regen_timer = Timer(lambda _: adv.charge_p("ds_sp", 0.0075, target=["s1", "s2"]), 0.99, True)
        sp_regen_buff = EffectBuff("ds_sp", 90, lambda: sp_regen_timer.on(), lambda: sp_regen_timer.off())
        Event("ds").listener(lambda _: sp_regen_buff.on())


class Gold_Fafnir(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        # disabled for convienance
        adv.dragonform.disabled = True


class Arsene(DragonBase):
    @property
    def ab(self):
        return super().ab if self.on_ele else [["s", 0.9]]


### SHADOW DRAGONS ###


class WeaponBase(EquipBase):
    def __init__(self, conf, c, qual):
        super().__init__(conf.w, c, qual)
        self.s3_conf = {sn: sconf for sn, sconf in conf.find(r"s3.*")}

    @property
    def s3(self):
        if self.on_ele or self.ele == "any":
            return self.s3_conf
        # if not self.on_ele:
        #     return None
        # if self.c.ele == 'light':
        #     return {**WeaponBase.AGITO_S3[self.c.ele], 's3_phase2': WeaponBase.LIGHT_S3P2[self.c.wt]}
        # else:
        #     return WeaponBase.AGITO_S3[self.c.ele]

    @property
    def ele(self):
        return self.conf.ele


APGroup = namedtuple("APGroup", ["value", "att", "restrict", "condition", "union", "qual"])


class AmuletPicker:
    UNION_THRESHOLD = {1: 4, 2: 4, 3: 4, 4: 3, 5: 2, 6: 2, 11: 2}

    def __init__(self):
        self._grouped = {5: {}, 4: {}}
        self._grouped_lookup = {}
        for qual, wp in wyrmprints.items():
            try:
                wpa_lst = next(iter(wp["a"]))
                wpa = wpa_lst[0]
                wpv = wpa_lst[1]
                try:
                    parts = wpa_lst[2].split("_")
                    wpc = tuple(c for c in parts if c not in ELEMENTS and c not in WEAPON_TYPES)
                    wpr = tuple(c for c in parts if c in ELEMENTS or c in WEAPON_TYPES)
                except (AttributeError, IndexError):
                    wpc = tuple()
                    wpr = tuple()
            except StopIteration:
                wpv = 0
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
            group_key = 5 if wp["rarity"] == 5 else 4
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
        while bis_i > 0 and (
            (group[bis_i].restrict and not (c.wt in group[bis_i].restrict or c.ele in group[bis_i].restrict))
            or (group[bis_i].condition and group[bis_i].condition and gval.condition != group[bis_i].condition)
            or (gval.union in retain_union and gval.union != group[bis_i].union)
        ):
            bis_i -= 1
        return bis_i

    def pick(self, amulets, c):
        retain_union = {}
        for u, thresh in AmuletPicker.UNION_THRESHOLD.items():
            u_sum = sum(a.union == u for a in amulets)
            if u_sum >= thresh:
                retain_union[u] = u_sum

        new_amulet_quals = set()
        for a_i, a in enumerate(amulets):
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
        "bleed": 0.15,
    }
    # actually depends on weapons kms
    RARITY_LIMITS = {6: 2, 5: 3, None: 2}
    PICKER = AmuletPicker()

    def __init__(self, confs, c, quals):
        limits = AmuletStack.RARITY_LIMITS.copy()
        self.an = []
        for conf, qual in zip(confs, quals):
            rk = 5 if conf["rarity"] == 5 else None
            if limits[rk] == 0:
                continue
            limits[rk] -= 1
            self.an.append(AmuletBase(conf, c, qual))
        # if any(limits.values()):
        #     raise ValueError("Unfilled wyrmprint slot")
        self.an = AmuletStack.PICKER.pick(self.an, c)
        self.an.sort(key=lambda a: (-a.rarity, a.name))
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

    @property
    def name_icon_lst(self):
        return chain(*((a.name, a.icon) for a in self.an))

    @property
    def escaped_icon_lst(self):
        return chain(*((a.escaped, a.icon) for a in self.an))

    @staticmethod
    def sort_ab(a):
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
        sorted_ab = defaultdict(lambda: [])
        # spf_ab = []
        for a in chain(*(a.ab for a in self.an)):
            if a[0] in limits:
                sorted_ab[a[0]].append(a)
            # elif a[0] == 'spf':
            #     spf_ab.append(a)
            else:
                merged_ab.append(a)

        for cat, lst in sorted_ab.items():
            for a in sorted(lst, key=AmuletStack.sort_ab):
                delta = min(limits[cat], a[1])
                limits[cat] -= delta
                # reminder: fix this too whenever buffcounts are fixed
                merged_ab.append((cat, delta, *a[2:]))
                if limits[cat] == 0:
                    break

        # if spf_ab and limits['sp'] > 0:
        #     for ab in sorted(spf_ab, key=AmuletStack.sort_ab):
        #         delta = min(limits['sp'], a[1])
        #         limits['sp'] -= delta
        #         merged_ab.append(('spf', delta, *a[2:]))
        #         if limits['sp'] == 0:
        #             break

        union_level = defaultdict(lambda: 0)
        for a in self.an:
            if a.union:
                union_level[a.union] += 1
        merged_ab.extend((("union", u, l) for u, l in union_level.items()))

        return merged_ab


class AmuletBase(EquipBase):
    KIND = "a"
    AUGMENTS = 50

    def __init__(self, conf, c, qual=None):
        super().__init__(conf, c, qual)

    @property
    def union(self):
        return self.conf.union

    @property
    def rarity(self):
        return self.conf.rarity


class Slots:
    DRAGON_DICTS = subclass_dict(DragonBase)

    DEFAULT_DRAGON = {
        "flame": "Gala_Mars",
        "water": "Gala_Reborn_Poseidon",
        "wind": "Gala_Reborn_Zephyr",
        "light": "Gala_Reborn_Jeanne",
        "shadow": "Gala_Cat_Sith",
    }

    # DEFAULT_WYRMPRINT = {
    #     'sword': ('The_Shining_Overlord', 'Primal_Crisis'),
    #     'blade': ('Resounding_Rendition', 'Breakfast_at_Valerios'),
    #     'dagger': ('Twinfold_Bonds', {
    #         'water': 'The_Prince_of_Dragonyule',
    #         'shadow': 'Howling_to_the_Heavens',
    #         'all': 'Levins_Champion'
    #     }),
    #     'axe': ('Kung_Fu_Masters', 'Breakfast_at_Valerios'),
    #     'lance': ('Resounding_Rendition', 'Breakfast_at_Valerios'),
    #     'wand': ('Candy_Couriers', 'Primal_Crisis'),
    #     'bow': ('Forest_Bonds', 'Primal_Crisis'),
    #     'staff': ('Resounding_Rendition', 'Breakfast_at_Valerios')
    # }
    DEFAULT_WYRMPRINT = [
        "Valiant_Crown",
        "The_Red_Impulse",
        "Memory_of_a_Friend",
        "Dueling_Dancers",
        "A_Small_Courage",
    ]

    AFFLICT_WYRMPRINT = {
        "flame": "Me_and_My_Bestie",
        "water": "His_Clever_Brother",
        "wind": "The_Fires_of_Hate",
        "light": "Spirit_of_the_Season",
        "shadow": "The_Fires_of_Hate",
    }

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

    def full_slot_icons(self):
        return ",".join(
            [
                self.c.escaped,
                self.c.icon,
                self.c.ele,
                self.c.wt,
                str(round(self.att)),
                self.d.escaped,
                self.d.icon,
                self.w.escaped,
                self.w.icon,
                *self.a.escaped_icon_lst,
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
        # self.c.oninit(adv)
        self.d.oninit(adv)
        # self.w.oninit(adv)
        # self.a.oninit(adv)
        for kind, slot in (("c", self.c), ("d", self.d), ("a", self.a), ("w", self.w)):
            for aidx, ab in enumerate(slot.ab):
                name = ab[0]
                if "_" in name:
                    acat = name.split("_")[0]
                else:
                    acat = name
                try:
                    self.abilities[f"{kind}_{aidx}_{name}"] = (
                        kind,
                        ability_dict[acat](*ab),
                    )
                except:
                    pass

        for name, val in self.abilities.items():
            kind, abi = val
            abi.oninit(adv, kind)
            self.abilities[name] = abi
