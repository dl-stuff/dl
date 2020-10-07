from itertools import chain, islice
from collections import defaultdict
from collections import namedtuple

from conf import wyrmprints, weapons, dragons, elecoabs, alias, ELEMENTS, WEAPON_TYPES
from core.config import Conf
from core.ability import ability_dict

def all_subclasses(cl):
    return set(cl.__subclasses__()).union([s for c in cl.__subclasses__() for s in all_subclasses(c)])

def subclass_dict(cl):
    return {sub_class.__name__: sub_class for sub_class in all_subclasses(cl)}

class SlotBase:
    KIND = 's'
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
        if self.conf['a']:
            return self.conf.a
        return []

    def oninit(self, adv):
        pass


class CharaBase(SlotBase):
    AUGMENTS = 100
    FAC_ELEMENT_ATT = {
        'all': {'altar1': 0.115, 'altar2': 0.115, 'slime': 0.04},
        'flame': {'tree': 0.26, 'arctos': 0.085},
        'water': {'tree': 0.16, 'yuletree': 0.085, 'dragonata': 0.085},
        'wind': {'tree': 0.16, 'shrine': 0.085},
        'light': {'tree': 0.16, 'retreat': 0.085, 'circus': 0.085},
        'shadow': {'tree': 0.26, 'library': 0.07}
    }
    FAC_ELEMENT_HP = FAC_ELEMENT_ATT.copy()
    FAC_ELEMENT_HP['flame']['arctos'] = 0.095
    FAC_ELEMENT_HP['water']['yuletree'] = 0.095
    FAC_ELEMENT_HP['water']['dragonata'] = 0.095
    FAC_ELEMENT_HP['wind']['shrine'] = 0.095
    FAC_ELEMENT_HP['light']['retreat'] = 0.095
    FAC_ELEMENT_HP['light']['circus'] = 0.095
    FAC_ELEMENT_HP['shadow']['library'] = 0.085

    FAC_WEAPON_ATT = {
        'all': {'dojo1': 0.15, 'dojo2': 0.15, 'weap': 0.225},
        'dagger': 0.05, 'bow': 0.05, 'blade': 0.05, 'wand': 0.05,
        'sword': 0.05, 'lance': 0.05, 'staff': 0.05, 'axe': 0.05,
        'gun': 0.0
    }
    FAC_WEAPON_HP = FAC_WEAPON_ATT.copy()

    NON_UNIQUE_COABS = ('Sword', 'Blade', 'Dagger', 'Bow', 'Wand', 'Axe2', 'Dagger2')
    MAX_COAB = 3 # max allowed coab, excluding self
    def __init__(self, conf, qual=None):
        super().__init__(conf, qual)
        self.coabs = {}
        self.coab_list = []
        self.coab_qual = None
        self.valid_coabs = elecoabs[self.ele]
        if self.conf['ex']:
            self.coabs[self.qual] = self.conf['ex']
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
                base_key = key.split('_')[-1]
                if any([ckey in base_key or base_key in ckey for ckey in self.coabs.keys()]):
                    continue
            self.coabs[key] = coab
            if key != self.coab_qual:
                self.coab_list.append(key)
                max_coabs -= 1
            chain, ex = coab
            if ex:
                ex_set.add(('ex', ex))
            if chain:
                full_ab.append(tuple(chain))
            if max_coabs == 0:
                break
        full_ab.extend(ex_set)
        if self.wt == 'axe':
            full_ab.append(('cc', 0.04))
        else:
            full_ab.append(('cc', 0.02))
        return full_ab


    @property
    def att(self):
        FE = CharaBase.FAC_ELEMENT_ATT
        FW = CharaBase.FAC_WEAPON_ATT
        halidom_mods = 1 + sum(FE['all'].values()) + sum(FE[self.ele].values()) + sum(FW['all'].values()) + FW[self.wt]
        return super().att * halidom_mods

    @property
    def hp(self):
        FE = CharaBase.FAC_ELEMENT_HP
        FW = CharaBase.FAC_WEAPON_HP
        halidom_mods = 1 + sum(FE['all'].values()) + sum(FE[self.ele].values()) + sum(FW['all'].values()) + FW[self.wt]
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
            return self.conf['ele'] == self.c.ele
        except:
            return False

    @property
    def att(self):
        return super().att * (1 + 0.5 * int(self.on_ele))

    @property
    def hp(self):
        return super().hp * (1 + 0.5 * int(self.on_ele))


class DragonBase(EquipBase):
    FAFNIR = 0.115
    DEFAULT_DCONF = {
        'duration': 10, # 10s dragon time
        'dracolith': 0.70, # base dragon damage
        'exhilaration': 0, # psiren aura
        'gauge_val': 100, # gauge regen value
        'latency': 0, # amount of delay for cancel
        'act': 'c3-s',

        'dshift.startup': 1.0,
        'dshift.recovery': 0.63333,
        'dshift.attr': [{'dmg': 2.0}],

        'dodge.startup': 0.66667,
        'dodge.recovery': 0,

        'end.startup': 0,
        'end.recovery': 0,
        'allow_end_cd': 4.0 # time before force end is allowed
    }
    def __init__(self, conf, c, qual=None):
        super().__init__(conf.d, c, qual)
        self.dragonform = conf

    def oninit(self, adv):
        from core.dragonform import DragonForm
        for dn, dconf in self.dragonform.items():
            if isinstance(dconf, dict):
                adv.damage_sources_check(dn, dconf)
        if adv.conf['dragonform']:
            name = self.c.name
            self.dragonform.update(adv.conf['dragonform'])
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


from core.modifier import EffectBuff, SingleActionBuff
from core.timeline import Timer, now
from core.log import log
### FLAME DRAGONS ###
class Gala_Mars(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        def shift_end_prep(e):
            adv.charge_p('shift_end',100)
        adv.Event('dragon_end').listener(shift_end_prep)
### FLAME DRAGONS ###

### WATER DRAGONS ###
class Gaibhne_and_Creidhne(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        charge_timer = Timer(lambda _: adv.charge_p('ds', 0.091, no_autocharge=True), 0.9, True)
        ds_buff = EffectBuff('ds_sp_regen_zone', 10, lambda: charge_timer.on(), lambda: charge_timer.off())
        adv.Event('ds').listener(lambda _: ds_buff.on())

class Nimis(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        def add_gauge_and_time(t):
            adv.dragonform.dragon_gauge += 200
            max_time = adv.dragonform.dtime() - adv.dragonform.conf.dshift.startup
            cur_time = adv.dragonform.shift_end_timer.timing - now()
            add_time = min(abs(max_time - cur_time), 5)
            adv.dragonform.shift_end_timer.add(add_time)
        adv.Event('ds').listener(add_gauge_and_time)

class Styx(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        adv.styx_spirit = 0
        adv.csd_buff = SingleActionBuff('d_compounding_sd',0.0,-1,'s','buff')
        def add_csd(e):
            if not adv.csd_buff.get():
                adv.csd_buff.set(min(2.00, adv.csd_buff.get()+0.50))
                adv.csd_buff.on()
            else:
                adv.csd_buff.value(min(2.00, adv.csd_buff.get()+0.50))
        csd_timer = Timer(add_csd, 15, True).on()
        def add_spirit(e):
            if e.index == 3:
                adv.styx_spirit = min(3, adv.styx_spirit+1)
                log('dx_spirit', adv.styx_spirit)
        adv.Event('dx').listener(add_spirit)
        def reset_spirit(e):
            adv.styx_spirit = 0
        adv.Event('ds').listener(reset_spirit)
        adv.Event('dragon_end').listener(reset_spirit)
### WATER DRAGONS ###

### WIND DRAGONS ###
class AC011_Garland(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        if adv.condition('maintain shield'):
            Timer(lambda _: adv.Modifier('d_1_dauntless','att','passive',0.30).on(), 15).on()

class Summer_Konohana_Sakuya(DragonBase):
    FLOWER_BUFFS = {
        1: (0.40, -1, 'att', 'buff'),
        2: (0.20, -1, 'defense', 'buff'),
        3: (0.50, -1, 's', 'buff'),
        4: (0.05, -1, 'res', 'water'),
        6: (0.20, -1, 'regen', 'buff')
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
                    f'd_sakuya_flower_{adv.summer_sakuya_flowers}',
                    *self.FLOWER_BUFFS[adv.summer_sakuya_flowers]
                ).on()
            except KeyError:
                pass
        add_flower()
        Timer(add_flower, 60, True).on()
        adv.Event('ds').listener(add_flower)
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
        adv.Event('dragon_end').listener(shift_end_energy)
### LIGHT DRAGONS ###

### SHADOW DRAGONS ###
class Gala_Cat_Sith(DragonBase):
    MAX_TRICKERY = 14
    def oninit(self, adv):
        super().oninit(adv)
        adv.trickery = Gala_Cat_Sith.MAX_TRICKERY
        threshold = 25
        self.trickery_buff = SingleActionBuff('d_trickery_buff', 1.80, 1, 's', 'buff').on()
        def add_trickery(t):
            adv.trickery = min(adv.trickery+t, Gala_Cat_Sith.MAX_TRICKERY)
            log('debug', 'trickery', f'+{t}', adv.trickery, adv.hits)
        def check_trickery(e=None):
            if adv.trickery > 0 and not self.trickery_buff.get():
                adv.trickery -= 1
                log('debug', 'trickery', '-1', adv.trickery)
                self.trickery_buff.on()
        def shift_end_trickery(e=None):
            if not adv.dragonform.is_dragondrive:
                add_trickery(8)
        adv.Event('dragon_end').listener(shift_end_trickery)
        if adv.condition('always connect hits'):
            add_combo_o = adv.add_combo
            self.thit = 0
            def add_combo(name='#'):
                add_combo_o(name)
                n_thit = adv.hits // threshold
                if n_thit > self.thit:
                    add_trickery(1)
                    self.thit = n_thit
                else:
                    n_thit = 0
                check_trickery()
            adv.add_combo = add_combo

class Fatalis(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        adv.dragonform.disabled = True

    @property
    def ab(self):
        return super().ab if self.on_ele else [['a', 0.5]]

class Nyarlathotep(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        def bloody_tongue(t=None):
            adv.Buff('bloody_tongue',0.30, 20).on()
        bloody_tongue(0)
        buff_rate = 90
        if adv.condition(f'hp=30% every {buff_rate}s'):
            buff_times = int(adv.duration // buff_rate)
            for i in range(1, buff_times):
                adv.Timer(bloody_tongue).on(buff_rate*i)

class Ramiel(DragonBase):
    def oninit(self, adv):
        super().oninit(adv)
        sp_regen_timer = Timer(lambda _: adv.charge_p('ds_sp', 0.0075, target=['s1', 's2']), 0.99, True)
        sp_regen_buff = EffectBuff('ds_sp', 90, lambda: sp_regen_timer.on(), lambda: sp_regen_timer.off())
        adv.Event('ds').listener(lambda _: sp_regen_buff.on())
### SHADOW DRAGONS ###


class WeaponBase(EquipBase):
    AGITO_S3 = {
        'flame': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': [['self', 0.40, -1, 'att', 'buff'], ['self', 1.00, -1, 'ctime', 'passive'], '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.05, -1, 'regen', 'buff', '-replace']}]}
        },
        'water': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': [['self', 0.20, -1, 'att', 'buff'], ['self', 0.12, -1, 'crit', 'chance'], '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.35, -1, 'defense', 'buff', '-replace']}]}
        },
        'wind': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': ['self', 0.40, -1, 'att', 'buff', '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.50, -1, 'defense', 'buff', '-replace']}]}
        },
        'light': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': ['self', 0.40, -1, 'att', 'buff', '-replace']}]}
        },
        'shadow': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': [['self', 0.30, -1, 'spd', 'passive'], ['self', 0.05, -1, 'crit', 'chance'], '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.40, -1, 'defense', 'buff', '-replace']}]}
        }
    }
    LIGHT_S3P2 = {
        'sword': {
            'startup': 0.1, 'recovery': 1.76667,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.43333},
                {'dmg': 1.984, 'dp': 100, 'iv': 0.63333},
                {'dmg': 1.984, 'iv': 0.8},
                {'dmg': 1.984, 'iv': 0.93333},
                {'dmg': 1.984, 'iv': 1.06667},
                {'dmg': 1.984, 'iv': 1.23333}
            ]
        },
        'blade': {
            'startup': 0.1, 'recovery': 2.2,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.43333},
                {'dmg': 1.704, 'dp': 100, 'iv': 0.33333},
                {'dmg': 1.704, 'iv': 0.63333},
                {'dmg': 1.704, 'iv': 0.8},
                {'dmg': 1.704, 'iv': 0.93333},
                {'dmg': 1.704, 'iv': 1.06667}
            ]
        },
        'dagger': {
            'startup': 0.1, 'recovery': 2.43333,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 2.2},
                {'dmg': 1.312, 'dp': 100, 'iv': 0.26667},
                {'dmg': 1.312, 'iv': 0.7},
                {'dmg': 1.312, 'iv': 1.1},
                {'dmg': 1.312, 'iv': 1.3},
                {'dmg': 1.312, 'iv': 1.6}
            ]
        },
        'axe': {
            'startup': 0.1, 'recovery': 2.1,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.56667},
                {'dmg': 2.26, 'dp': 100, 'iv': 0.66667},
                {'dmg': 2.26, 'iv': 0.9},
                {'dmg': 2.26, 'iv': 1.2},
                {'dmg': 2.26, 'iv': 1.43333},
                {'dmg': 2.26, 'iv': 1.5}
            ]
        },
        'lance': {
            'startup': 0.1, 'recovery': 3.23333,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 2.5},
                {'dmg': 1.656, 'dp': 100, 'iv': 0.86667},
                {'dmg': 1.656, 'iv': 0.96667},
                {'dmg': 1.656, 'iv': 1.9},
                {'dmg': 1.656, 'iv': 2.0},
                {'dmg': 1.656, 'iv': 2.1}
            ]
        },
        'bow': {
            'startup': 0.1, 'recovery': 2.0,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.53333},
                {'dmg': 1.898, 'dp': 100, 'iv': 0.66667, 'msl': 1},
                {'dmg': 1.898, 'iv': 0.8, 'msl': 1},
                {'dmg': 1.898, 'iv': 0.9, 'msl': 1},
                {'dmg': 1.898, 'iv': 1.5, 'msl': 1},
                {'dmg': 1.898, 'iv': 1.53333, 'msl': 1}
            ]
        },
        'wand': {
            'startup': 0.1, 'recovery': 1.66667,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.36667},
                {'dmg': 2.168, 'dp': 100, 'iv': 0.96667},
                {'dmg': 2.168, 'iv': 1.06667},
                {'dmg': 2.168, 'iv': 1.13333},
                {'dmg': 2.168, 'iv': 1.26667},
                {'dmg': 2.168, 'iv': 1.26667}
            ]
        },
        'staff': {
            'startup': 0.1, 'recovery': 1.4,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.36667},
                {'dmg': 1.51, 'dp': 100, 'iv': 0.83333},
                {'dmg': 1.51, 'iv': 1.0},
                {'dmg': 1.51, 'iv': 1.16667},
                {'dmg': 1.51, 'iv': 1.33333},
                {'dmg': 1.51, 'iv': 1.36667}
            ]
        },
        'gun': {
            'startup': 0.1, 'recovery': 1.93333,
            'attr': [
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.5},
                {'dmg': 0.44, 'killer': [0.5, ['paralysis']], 'dp': 100, 'iv': 0.66667, 'msl': 1},
                {'dmg': 0.44, 'killer': [0.5, ['paralysis']], 'iv': 0.66667, 'msl': 1}, 4,
                {'dmg': 0.44, 'killer': [0.5, ['paralysis']], 'iv': 0.86667, 'msl': 1}, 5,
                {'dmg': 0.44, 'killer': [0.5, ['paralysis']], 'iv': 1.06667, 'msl': 1}, 5,
                {'dmg': 0.44, 'killer': [0.5, ['paralysis']], 'iv': 1.26667, 'msl': 1}, 5,
                {'dmg': 0.44, 'killer': [0.5, ['paralysis']], 'iv': 1.46667, 'msl': 1}, 5
            ]
        }
    }
    def __init__(self, conf, c, qual=None):
        qual = (c.ele, c.wt)
        super().__init__(conf, c, qual)

    @property
    def s3(self):
        if not self.on_ele:
            return None
        if self.c.ele == 'light':
            return {**WeaponBase.AGITO_S3[self.c.ele], 's3_phase2': WeaponBase.LIGHT_S3P2[self.c.wt]}
        else:
            return WeaponBase.AGITO_S3[self.c.ele]

    @property
    def ele(self):
        return self.conf.ele

APGroup = namedtuple('APGroup', ['value', 'att', 'restrict', 'condition', 'union', 'qual'])
class AmuletPicker:
    UNION_THRESHOLD = {1: 4, 2: 4, 3: 4, 4: 3, 5: 2, 6: 2, 11: 2}
    def __init__(self):
        self._grouped = {5: {}, 4: {}}
        self._grouped_lookup = {}
        for qual, wp in wyrmprints.items():
            try:
                wpa_lst = next(iter(wp['a']))
                wpa = wpa_lst[0]
                wpv = wpa_lst[1]
                try:
                    parts = wpa_lst[2].split('_')
                    wpc = tuple(c for c in parts if c not in ELEMENTS and c not in WEAPON_TYPES)
                    wpr = tuple(c for c in parts if c in ELEMENTS or c in WEAPON_TYPES)
                except (IndexError, AttributeError):
                    wpc = tuple()
                    wpr = tuple()
            except StopIteration:
                wpv = 0
                wpa = (None,)
                wpc = None
                wpr = None
            grouped_value = APGroup(value=wpv, att=wp['att'], restrict=wpr, condition=wpc, union=wp['union'], qual=qual)
            group_key = 5 if wp['rarity'] == 5 else 4
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
        
        while bis_i >= 0 and group[bis_i].restrict and not (c.wt in group[bis_i].restrict or c.ele in group[bis_i].restrict):
                bis_i -= 1
        if group[bis_i].condition:
            while bis_i >= 0 and group[bis_i].condition and gval.condition != group[bis_i].condition:
                bis_i -= 1
        if gval.union in retain_union:
            while gval.union != group[bis_i].union:
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


class AmuletQuint:
    AB_LIMITS = {
        'a': 0.20, 's': 0.40, 'cc': 0.15, 'cd': 0.25,
        'fs': 0.50, 'bt': 0.30, 'sp': 0.15, 'bk': 0.30,
        'od': 0.15, 'lo_att': 0.60, 'ro_att': 0.10,
        'bc_att': 0.15, 'bc_cd': 0.15, 'bc_energy': 1, 'bc_regen': 3,
        'prep': 100, 'dc': 3, 'dcs': 3, 'da': 0.18, 'dt': 0.20,
        'k_burn': 0.30, 'k_poison': 0.25, 'k_paralysis': 0.25,
        'k_frostbite': 0.25, 'k_stun': 0.25, 'k_sleep': 0.25
    }
    # actually depends on weapons kms
    RARITY_LIMITS = {5: 3, None: 2}
    PICKER = AmuletPicker()
    def __init__(self, confs, c, quals):
        limits = AmuletQuint.RARITY_LIMITS.copy()
        self.an = []
        for conf, qual in zip(confs, quals):
            rk = 5 if conf['rarity'] == 5 else None
            if limits[rk] == 0:
                continue
            limits[rk] -= 1
            self.an.append(AmuletBase(conf, c, qual))
        if any(limits.values()):
            raise ValueError('Unfilled wyrmprint slot')
        self.an = AmuletQuint.PICKER.pick(self.an, c)
        self.an.sort(key=lambda a: (-a.rarity, a.name))
        self.c = c

    def __str__(self):
        return '+'.join(map(str, self.an))

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

    @staticmethod
    def sort_ab(a):
        if len(a) <= 2:
            return -100 * a[1]
        if 'hp' not in a[2]:
            return -1 * a[1]
        return a[1]

    @property
    def ab(self):
        merged_ab = []

        limits = AmuletQuint.AB_LIMITS.copy()
        sorted_ab = defaultdict(lambda: [])
        spf_ab = []
        for a in chain(*(a.ab for a in self.an)):
            if a[0] in limits:
                sorted_ab[a[0]].append(a)
            elif a[0] == 'spf':
                spf_ab.append(a)
            else:
                merged_ab.append(a)

        for cat, lst in sorted_ab.items():
            for a in sorted(lst, key=AmuletQuint.sort_ab):
                delta = min(limits[cat], a[1])
                limits[cat] -= delta
                merged_ab.append((cat, delta, *a[2:]))
                if limits[cat] == 0:
                    break

        if spf_ab and limits['sp'] > 0:
            for ab in sorted(spf_ab, key=AmuletQuint.sort_ab):
                delta = min(limits['sp'], a[1])
                limits['sp'] -= delta
                merged_ab.append(('spf', delta, *a[2:]))
                if limits['sp'] == 0:
                    break

        union_level = defaultdict(lambda: 0)
        for a in self.an:
            if a.union:
                union_level[a.union] += 1
        merged_ab.extend((('union', u, l) for u, l in union_level.items()))

        return merged_ab


class AmuletBase(EquipBase):
    KIND = 'a'
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
        'flame': 'Gala_Mars',
        'water': 'Gaibhne_and_Creidhne',
        'wind': 'Midgardsormr_Zero',
        'light': 'Daikokuten',
        'shadow': 'Gala_Cat_Sith'
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
        'Valiant_Crown',
        'The_Red_Impulse',
        'Memory_of_a_Friend',
        'Dueling_Dancers',
        'A_Small_Courage'
    ]

    AFFLICT_WYRMPRINT = {
        'flame': 'Me_and_My_Bestie',
        'water': 'His_Clever_Brother',
        'wind': 'The_Fires_of_Hate',
        'light': 'Spirit_of_the_Season',
        'shadow': 'The_Fires_of_Hate'
    }

    def __init__(self, name, conf, sim_afflict=None, flask_env=False):
        self.c = CharaBase(conf, name)
        self.sim_afflict = sim_afflict
        self.flask_env = flask_env
        self.d = None
        self.w = None
        self.a = None
        self.abilities = {}

    def __str__(self):
        return ','.join([
            self.c.name,
            self.c.ele, self.c.wt, str(round(self.att)),
            self.d.name,
            self.w.name,
            *self.a.name_lst
        ])

    def full_slot_icons(self):
        return ','.join([
            self.c.name, self.c.icon,
            self.c.ele, self.c.wt, str(round(self.att)),
            self.d.name, self.d.icon,
            self.w.name, self.w.icon,
            *self.a.name_icon_lst
        ])

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
        conf = Conf(weapons[self.c.ele][self.c.wt])
        self.w = WeaponBase(conf, self.c)

    def set_a(self, keys=None):
        if keys is None or len(keys) < 5:
            keys = list(set(Slots.DEFAULT_WYRMPRINT))
        else:
            keys = list(set(keys))
        # if len(keys) < 5:
        #     raise ValueError('Less than 5 wyrmprints equipped')
        confs = [Slots.get_with_alias(wyrmprints, k)[0] for k in keys]
        self.a = AmuletQuint(confs, self.c, keys)

    def set_slots(self, confslots):
        for t in ('d', 'w', 'a'):
            getattr(self, f'set_{t}')(confslots[t])

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
        for kind, slot in (('c', self.c), ('d', self.d), ('a', self.a), ('w', self.w)):
            for aidx, ab in enumerate(slot.ab):
                name = ab[0]
                if '_' in name:
                    acat = name.split('_')[0]
                else:
                    acat = name
                try:
                    self.abilities[f'{kind}_{aidx}_{name}'] = (kind, ability_dict[acat](*ab))
                except:
                    pass

        for name, val in self.abilities.items():
            kind, abi = val
            abi.oninit(adv, kind)
            self.abilities[name] = abi


if __name__ == '__main__':
    from conf import get_adv, load_all_equip_json
    # amulet_qual = [
    #     'The_Wyrmclan_Duo',
    #     'Flash_of_Genius',
    #     'Moonlight_Party',
    #     'The_Plaguebringer',
    #     'His_Clever_Brother'
    # ]
    for adv, equip in load_all_equip_json().items():
        conf = get_adv(adv)
        pref = equip['180']['pref']
        a_qual = equip['180'][pref]['slots.a']
        slots = Slots(adv, conf.c)
        slots.set_a(keys=a_qual)
