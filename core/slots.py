from itertools import chain
from collections import defaultdict
import html

from conf import (
    SELF,
    load_drg_json,
    load_json,
    wyrmprints,
    wyrmprints_meta,
    weapons,
    subclass_dict,
    get_icon,
)
from core.config import Conf
from core.ability import make_ability
from core.modifier import Modifier


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
    def coab_list(self):
        return self.coabs.keys()

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

        lim_groups = wyrmprints_meta["lim_groups"]
        shift_groups = wyrmprints_meta["shift_groups"]
        actconds = wyrmprints_meta["actconds"]
        unions = wyrmprints_meta["unions"]

        shift_abilities = defaultdict(list)
        mix_abilities = defaultdict(list)
        psalm_abilities = []

        for ability in chain(*(a.abilities for a in self.an)):
            merged = True
            if shiftgroup := ability.get("shiftgroup"):
                shift_abilities[shiftgroup].append(ability["id"])
                merged = False
            elif (lg := ability["lg"]) and (lg_info := lim_groups[lg]) and lg_info["mix"]:
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
            merged_abilities.extend(to_ability[str(sum_level)])

        for lg, abilities in mix_abilities.items():
            if len(abilities) == 1:
                del abilities[0]["lg"]
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
            del mix_ability["lg"]
            merged_abilities.append(mix_ability)

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
        "flame": "Gala_Reborn_Agni",
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
        for slot in (self.c, self.d, self.w):
            for ab in slot.abilities:
                if ability := make_ability(adv, ab):
                    self.abilities.append(ability)
            adv.actconds.update(slot.actconds)
        for ab in self.a.abilities:
            if ability := make_ability(adv, ab, use_limit=True):
                self.abilities.append(ability)
        adv.actconds.update(self.a.actconds)
