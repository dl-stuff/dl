from itertools import chain
from collections import defaultdict
import html

from conf import (
    load_drg_json,
    load_json,
    wyrmprints,
    weapons,
    subclass_dict,
    get_icon,
)
from core.config import Conf
from core.ability import Ability


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
    def abilities(self):
        if self.conf["abilities"]:
            return self.conf.abilities
        return []

    @property
    def actconds(self):
        if self.conf["actconds"]:
            return self.conf.actconds
        return {}

    def oninit(self, adv):
        pass


class ExBase:
    DATA = load_json("exability.json")
    GENERICS = {
        "Lance": ["101010010", None],
        "Blade": ["101020010", None],
        "Axe": ["101030010", None],
        "Bow": ["101040010", None],
        "Sword": ["101050010", None],
        "Wand": ["102000010", None],
        "Dagger": ["103000010", None],
        "Staff": ["104000010", None],
        "Gun": ["109000009", None],
    }
    UNIQUE = {
        "HpDef": ["101060010", None],
        "AtkSpd": ["101100007", None],
        "ScorchrendBoost": ["103150005", None],
        "Wand2": ["106000008", None],
        "ForceStrike": ["106000016", None],
        "Dagger2": ["106070008", None],
        "Debuff": ["106080008", None],
        "Bufftime": ["118000008", None],
        "ParalysisPunish": ["120040008", None],
        "Axe2": ["126000008", None],
        "DragonBoost": ["136000008", None],
    }
    LOOKUP = DATA["lookup"]
    LOOKUP.update(GENERICS)
    LOOKUP.update(UNIQUE)

    def __init__(self, qual) -> None:
        self.coab_id, self.chain_id = self.LOOKUP[qual]
        self.coab = self.DATA["coab"][self.coab_id]
        self.chain = self.DATA["chain"][self.chain_id]


class CharaBase(SlotBase):
    AUGMENTS = 100
    FORT = load_json("fort.json")
    # album_false album_true None
    FORT_KEY = "album_false"

    MAX_COAB = 3  # max allowed coab, excluding self

    def __init__(self, conf, qual=None):
        super().__init__(conf, qual)
        self.coabs = {self.qual: ExBase(self.qual)}
        self.base_id = self.icon[0:6]

    def set_coabs(self, coab_list):
        self.coabs = {self.qual: ExBase(self.qual)}
        seen_base_id = {self.base_id}
        for coab in sorted(coab_list):
            base_id = get_icon(coab)[0:6]
            if base_id in seen_base_id:
                continue
            seen_base_id.add(base_id)
            try:
                self.coabs[coab] = ExBase(coab)
            except KeyError:
                pass

    @property
    def abilities(self):
        chara_ab = list(super().abilities)
        coab_abs = {}
        for ex in self.coabs.values():
            if "ab" in ex.coab:
                coab_abs[ex.coab["category"]] = ex.coab
            chara_ab.extend(ex.chain)
        chara_ab.extend(coab_abs.values())
        return chara_ab

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
            "dacl": "ds1,x=3",  # the default dacl
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
        unique_dform = False
        if adv.conf["dragonform"]:
            name = self.c.name
            self.dform = Conf(adv.conf["dragonform"])
            unique_dform = True
        else:
            name = self.name
        self.dform.update(DragonBase.DEFAULT_DCONF, rebase=True)

        if self.c.conf["utp"]:
            from core.dragonform import DragonFormUTP

            adv.dragonform = DragonFormUTP(name, self.dform, adv, self)
        else:
            from core.dragonform import DragonForm

            adv.dragonform = DragonForm(name, self.dform, adv, self, unique_dform=unique_dform)
        self.adv = adv
        return unique_dform

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
    def abilities(self):
        return super().abilities if self.on_ele else []


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
    def update_gozu_tenno_buff(self, t):
        # will ignore cd of 15s for qol reasons
        self.adv.gozu_tenno_buff.on(30)

    def oninit(self, adv):
        super().oninit(adv)
        adv.gozu_tenno_buff = adv.Selfbuff("gozu_tenno_buff", 0.3, 30, "flame", "ele").no_bufftime()

        self.fs_charging_timer = Timer(self.update_gozu_tenno_buff, 3.0 - 0.00001, True)

        Event("fs_start").listener(lambda _: self.fs_charging_timer.on(), order=0)
        Event("fs_end").listener(lambda _: self.fs_charging_timer.off(), order=0)


class Gala_Reborn_Agni(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gagni_buff", "flame")


### FLAME DRAGONS ###

### WATER DRAGONS ###
class Nimis(DragonBase):
    def ds1_proc(self, e):
        self.adv.dragonform.charge_dprep(20)
        self.adv.dragonform.extend_shift_time(5, percent=False)


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

    def ds1_proc(self, e):
        self.add_flower()

    def oninit(self, adv):
        super().oninit(adv)
        adv.summer_sakuya_flowers = 0
        self.flower_buffs = Summer_Konohana_Sakuya.FLOWER_BUFFS
        if adv.nihilism:
            self.flower_buffs = Summer_Konohana_Sakuya.FLOWER_BUFFS_NIHIL

        self.add_flower()
        Timer(self.add_flower, 60, True).on()


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
    def add_rage(self, e=None):
        self.adv.moonlit_rage = min(10, self.adv.moonlit_rage + 1)
        log("moonlit_rage", "+1", self.adv.moonlit_rage, 10, "auto" if e is None else "dfs")

    def d_moon_repeat(self, t):
        self.add_rage("auto")
        self.adv.dmg_make("dmoon", 2.58)
        self.adv.add_combo()
        self.adv.add_hp(10)

    def ds1_proc(self, e):
        if e.group == 0:
            self.add_rage("auto")
            self.blood_moon_timer.on()
            self.adv.charge_p("ds1", 100, target="ds1", dragon_sp=True)
        else:
            self.blood_moon_timer.off()
            self.adv.blood_moon = 0
            self.adv.moonlit_rage = 0
            self.adv.a_s_dict["ds1"].set_enabled(False)

    def dfs_start(self, e):
        self.dragon_strike_timer.on()

    def dfs_charged(self, e):
        self.dragon_strike_timer.off()

    def shift_end_proc(self, _=None):
        if self.dragon_strike_timer is not None:
            self.dragon_strike_timer.off()
        SelfAffliction("gala_beast_volk_poison", -10, [12, 2.9], affname="poison").on()

    def oninit(self, adv):
        self.dragon_strike_timer = None
        if not super().oninit(adv):
            self.adv.blood_moon = 0
            self.adv.moonlit_rage = 0
            self.blood_moon_timer = Timer(self.d_moon_repeat, 3.5, True)
            self.dragon_strike_timer = Timer(self.add_rage, 1.0, True)

            Event("dfs_start").listener(self.dfs_start)
            Event("dfs_charged").listener(self.dfs_charged)
        Event("divinedragon_end").listener(self.shift_end_proc)


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


class Gala_Chronos_Nyx(DragonBase):
    def oninit(self, adv):
        if not super().oninit(adv):
            adv.dragonform.untimed_shift = True


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
        if adv.dragonform.dform_mode == -1:
            adv.dragonform.set_disabled("Fatalis")

    @property
    def abilities(self):
        return super().abilities if self.on_ele else [["a", 0.5]]


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
        if adv.dragonform.dform_mode == -1:
            adv.dragonform.set_disabled("Gold_Fafnir")


class Arsene(DragonBase):
    @property
    def abilities(self):
        return super().abilities if self.on_ele else [["s", 0.9]]


class Gala_Reborn_Nidhogg(Gala_Reborn):
    def oninit(self, adv):
        super().oninit(adv, "gnidhogg_buff", "shadow")


class Gala_Bahamut(DragonBase):
    def force_dp_amount(self, _):
        self.adv.dragonform.max_dragon_gauge = 1000
        self.adv.dragonform.charge_dprep(50)
        if self.adv.dragonform.dform_mode == -1:
            self.adv.dragonform.shift_cost = 1000

    def oninit(self, adv):
        super().oninit(adv)
        self.adv.dragonform.max_dragon_gauge = 0
        Timer(self.force_dp_amount, 0.0001).on()


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


class AmuletStack:
    # actually depends on weapon but i choose to not care
    META = load_json("wyrmprints_meta.json")
    RARITY_LIMITS = {1: 3, 2: 2, 3: 2}

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
        # self.an = AmuletStack.PICKER.pick(self.an, c)
        self.an.sort(key=lambda a: (a.rarity, a.name))
        self.c = c
        self.actconds = {}

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

    @property
    def abilities(self):
        self.actconds = {}
        merged_abilities = []

        lim_groups = AmuletStack.META["lim_groups"]
        shift_groups = AmuletStack.META["shift_groups"]
        actconds = AmuletStack.META["actconds"]

        shift_abilities = defaultdict(list)
        mix_abilities = defaultdict(list)
        psalm_abilities = []

        for ability in chain(*(a.abilities for a in self.an)):
            merged = True
            if shiftgroup := ability.get("shiftgroup"):
                shift_abilities[shiftgroup].append(ability["id"])
                merged = False
            elif (lg := ability["lg"]) and lg in lim_groups:
                mix_abilities[lg].append(ability)
                merged = False
            elif ablst := ability["ab"]:
                for ab in ablst:
                    if ab[0] == "psalm":
                        psalm_abilities.append(ab)
                        if len(ablst) == 1:
                            merged = False
                    elif ab[0] == "actcond":
                        for actcond_id in ab[2:]:
                            self.actconds[actcond_id] = actconds[actcond_id]
                    elif ab[0] == "hitattr":
                        actcond_id = ab[1]["actcond"]
                        self.actconds[actcond_id] = actconds[actcond_id]
            if merged:
                merged_abilities.append(ability)

        for shift, abilities in shift_abilities.items():
            to_level, to_ability = shift_groups[shift]
            sum_level = min(max(to_level.values()), sum((to_level[abid] for abid in abilities)))
            merged_abilities.append(to_ability[str(sum_level)])

        for lg, abilities in mix_abilities.items():
            if len(abilities) == 1:
                merged_abilities.append(abilities[0])
                continue
            actcond_duration = 0
            actcond_target = None
            actcond_mods_to_mix = defaultdict(float)
            for ability in abilities:
                actcond_target = ability["ab"][0][1]
                actcond = actconds[ability["ab"][0][2]]
                actcond_duration = max(actcond_duration, actcond["duration"])
                for mod in actcond["mods"]:
                    actcond_mods_to_mix[tuple(mod[1:])] += mod[0]
            actcond_mods = []
            for modto, value in actcond_mods_to_mix.items():
                actcond_mods.append([min(value, lim_groups[lg]["max"]), *modto])
            mix_ability = dict(abilities[0])
            mix_ability["ab"] = [["actcond", actcond_target, {"duration": actcond_duration, "mods": actcond_mods}]]
            merged_abilities.append(mix_ability)

        unions = AmuletStack.META["unions"]
        union_counter = defaultdict(int)
        for amulet in self.an:
            if amulet.union:
                union_counter[amulet.union] += 1
        for _, union, min_count, add_count in psalm_abilities:
            if union_counter.get(union, 0) >= min_count:
                union_counter[union] += add_count
        for union, count in union_counter.items():
            union_data = unions[str(union)]
            try:
                merged_abilities.extend(union_data[str(count)])
            except KeyError:
                max_count, max_ab = max(union_data.items())
                if count > int(max_count):
                    merged_abilities.extend(max_ab)

        return merged_abilities


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
        "Memory_of_a_Friend",
        "Moonlight_Party",
        "Worthy_Rivals",
        "A_Small_Courage",
        "Dueling_Dancers",
        "Mask_of_Determination_Bow",
        "Applelicious_Dreams",
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

    def set_d(self, key=None):
        if not key:
            key = Slots.DEFAULT_DRAGON[self.c.ele]
        conf = Conf(load_drg_json(key))
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
        if keys is None or len(keys) < 7:
            keys = list(set(Slots.DEFAULT_WYRMPRINT))
        else:
            keys = list(set(keys))
        confs = [Conf(wyrmprints[k]) for k in keys]
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
        self.abilities = []
        for kind, slot in (("c", self.c), ("d", self.d), ("a", self.a), ("w", self.w)):
            for ab in slot.abilities:
                try:
                    self.abilities.append(Ability(adv, ab))
                except:
                    pass
            adv.update(slot.actconds)
