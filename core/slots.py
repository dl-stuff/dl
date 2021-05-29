from itertools import chain
from collections import defaultdict, namedtuple
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
    FAC_ELEMENT_ATT = {
        "all": {"altar": 0.26, "slime": 0.04},
        "flame": {"tree": 0.31, "arctos": 0.085},
        "water": {"tree": 0.31, "yuletree": 0.085, "dragonata": 0.085},
        "wind": {"tree": 0.31, "shrine": 0.085},
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
        "gun": 0.075,  # opera (0.05) + fount (0.05) - diff in weap (0.225 - 0.200 = 0.025)
    }
    FAC_WEAPON_HP = FAC_WEAPON_ATT.copy()

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
            "gauge_val": 10,  # gauge regen percent
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

        if adv.conf["dragonform"]:
            name = self.c.name
            self.dragonform = Conf(adv.conf["dragonform"])
        else:
            name = self.name

        for dn, dconf in self.dragonform.items():
            if isinstance(dconf, dict):
                adv.hitattr_check(dn, dconf)

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
class Gaibhne_and_Creidhne(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        if not adv.nihilism:
            charge_timer = Timer(lambda _: adv.charge_p("ds", 0.091, no_autocharge=False), 0.9, True)
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
            adv.dragonform.charge_gauge(20, percent=True, dhaste=False)
            adv.dragonform.set_shift_end(5, percent=False, addition=True)

        Event("ds").listener(add_gauge_and_time)


class Styx(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)

        if not adv.nihilism:
            adv.csd_buff = SingleActionBuff("d_compounding_sd", 0.0, -1, "s", "buff")

            def add_csd(e):
                if not adv.csd_buff.get():
                    adv.csd_buff.set(min(2.00, adv.csd_buff.get() + 0.50))
                    adv.csd_buff.on()
                else:
                    adv.csd_buff.value(min(2.00, adv.csd_buff.get() + 0.50))

            Timer(add_csd, 15, True).on()

            def add_spirit(e):
                if e.index == 3:
                    adv.styx_spirit = min(3, adv.styx_spirit + 1)
                    log("dx_spirit", adv.styx_spirit)

            Event("dx").listener(add_spirit)

        adv.styx_spirit = 0

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
        self.flower_buffs = Summer_Konohana_Sakuya.FLOWER_BUFFS
        if adv.nihilism:
            self.flower_buffs = dict(self.flower_buffs)
            del self.flower_buffs[1]
            del self.flower_buffs[2]
            del self.flower_buffs[3]

        def add_flower(t=None):
            if adv.summer_sakuya_flowers >= 6:
                return
            adv.summer_sakuya_flowers += 1
            try:
                adv.Selfbuff(
                    f"d_sakuya_flower_{adv.summer_sakuya_flowers}",
                    *self.flower_buffs[adv.summer_sakuya_flowers],
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


class Rose_Queen(DragonBase):
    # {'_ArmorBreakLv': 4,
    #   '_Attributes03': 1,
    #   '_Attributes08': 1,
    #   '_DamageAdjustment': 0.5,
    #   '_DamageMotionTimeScale': 1.2000000476837158,
    #   '_FontEffect': 'EFF_FNT_COMMON_ATK_02',
    #   '_HeadText': 'ACTION_CONDITION_0',
    #   '_HitExecType': 1,
    #   '_Id': 'S152_002_00_LV02',
    #   '_InvincibleBreakLv': 2,
    #   '_KnockBackDurationSec': 0.30000001192092896,
    #   '_KnockBackType': 1,
    #   '_SplitDamageCount': 3,
    #   '_TargetGroup': <ActionTargetGroup.HOSTILE: 3>,
    #   '_ToBreakDmgRate': 1.0,
    #   '_ToOdDmgRate': 1.0,
    #   '_UseDamageMotionTimeScale': 1}
    #  {'_ArmorBreakLv': 4,
    #    '_DamageMotionTimeScale': 1.2000000476837158,
    #    '_HeadText': 'ACTION_CONDITION_0',
    #    '_HitExecType': 2,
    #    '_Id': 'S152_002_01_LV02',
    #    '_InvincibleBreakLv': 2,
    #    '_RecoveryValue': 10,
    #    '_SplitDamageCount': 3,
    #    '_TargetGroup': <ActionTargetGroup.FIXED_OBJECT: 16>,
    #    '_UseDamageMotionTimeScale': 1}
    def oninit(self, adv):
        super().oninit(adv)

        try:
            o_ds_proc = getattr(adv, "ds_proc")
        except AttributeError:
            o_ds_proc = None

        def ds_proc_slayer(e):
            log("ds_proc_slayer", "wweeeee")
            if o_ds_proc:
                o_ds_proc()
            e = adv.Event("slayed")
            e.count = 25
            e.name = "dx"
            e()

        adv.ds_proc = ds_proc_slayer


### WIND DRAGONS ###

### LIGHT DRAGONS ###
class Gala_Thor(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        if not adv.nihilism:

            def chariot_energy(t):
                adv.energy.add(1)

            Timer(chariot_energy, 5, True).on()

            def shift_end_energy(e):
                adv.energy.add(5, team=True)

            Event("dragon_end").listener(shift_end_energy)


class Lumiere_Pandora(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        if not adv.nihilism:
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
        if not adv.nihilism:
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
        while bis_i > 0 and (
            (group[bis_i].restrict and not (c.wt in group[bis_i].restrict or c.ele in group[bis_i].restrict))
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
                    self.abilities[f"ab_{kind}{aidx}"] = ability_dict[acat](*ab)
                except:
                    pass

        for key, ab in self.abilities.items():
            ab.oninit(adv, key)
