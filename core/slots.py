from itertools import chain
from collections import defaultdict

from conf import wyrmprints, weapons, load_drg_json, coability_dict
from core.config import Conf


def all_subclasses(c):
    return set(c.__subclasses__()).union([s for c in c.__subclasses__() for s in all_subclasses(c)])

def subclass_dict(c):
    return {sub_class.__name__: sub_class for sub_class in all_subclasses(c)}


class SlotBase:
    AUGMENTS = 0
    def __init__(self, conf):
        self.conf = conf

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
        return self.conf.a

    def oninit(self, adv):
        pass


class CharaBase(SlotBase):
    AUGMENTS = 100
    FAC_ELEMENT = {
        'all': {'altar1': 0.115, 'altar2': 0.115, 'slime': 0.04},
        'flame': {'tree': 0.26, 'arctos': 0.085},
        'water': {'tree': 0.16, 'yuletree': 0.085, 'dragonata': 0.085},
        'wind': {'tree': 0.16, 'shrine': 0.085},
        'light': {'tree': 0.16, 'retreat': 0.085, 'circus': 0.085},
        'shadow': {'tree': 0.26, 'library': 0.07}
    }
    FAC_WEAPON = {
        'all': {'dojo1': 0.15, 'dojo2': 0.15},
        'dagger': 0.05, 'bow': 0.05, 'blade': 0.05, 'wand': 0.05,
        'sword': 0.05, 'lance': 0.05, 'staff': 0.05, 'axe': 0.05
    }
    def __init__(self, conf):
        super().__init__(conf)
        self.coabs = {}
        self.valid_coabs = coability_dict(self.ele)

        try:
            coab = self.valid_coabs[self.name]
            chain = coab[0]
            if chain is None or len(chain)<3 or chain[2] != 'hp≤40':
                self.coabs[self.name] = coab
        except:
            try:
                upper_wt = self.wt[0].upper() + wt[1:].lower()
                self.coabs[upper_wt] = self.valid_coabs[upper_wt]
            except:
                pass

    @property
    def att(self):
        FE = CharaBase.FAC_ELEMENT
        FW = CharaBase.FAC_WEAPON
        halidom_mods = 1 + sum(FE['all'].values()) + sum(FE[self.ele].values()) + sum(FW['all'].values()) + FW[self.wt]
        return super().att * halidom_mods

    # @property
    # def hp(self):
    #     # FIXME - halidom calcs
    #     return self.conf.hp + self.AUGMENTS

    @property
    def ele(self):
        return self.conf.ele

    @property
    def wt(self):
        return self.conf.wt


class EquipBase(SlotBase):
    def __init__(self, conf, c):
        super().__init__(conf)
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
    def __init__(self, conf, c):
        super().__init__(conf.d, c)
        self.dragonform = conf

    @property
    def att(self):
        return super().att * (1 + DragonBase.FAFNIR)

    # @property
    # def hp(self):
    #     # FIXME - halidom calcs
    #     return self.conf.hp + self.AUGMENTS

class WeaponBase(EquipBase):
    AGITO_S3 = {
        'flame': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': [['self', 0.20, -1, 'att', 'buff'], ['self', 1.00, -1, 'ctime', 'passive'], '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.05, -1, 'regen', 'buff', '-replace']}]}
        },
        'water': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': ['self', 0.20, -1, 'crit', 'chance', '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.35, -1, 'defense', 'buff', '-replace']}]}
        },
        'wind': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': ['self', 0.25, -1, 'att', 'buff', '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.50, -1, 'defense', 'buff', '-replace']}]}
        },
        'light': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': ['self', 0.20, -1, 'att', 'buff', '-replace']}]}
        },
        'shadow': {
            's3': {'sp' : 3000, 'startup' : 0.25, 'recovery' : 0.90},
            's3_phase1': {'attr': [{'buff': [['self', 0.30, 'spd', 'passive', -1], ['self', 0.05, -1, 'crit', 'chance'], '-replace']}]},
            's3_phase2': {'attr': [{'buff': ['self', 0.40, -1, 'defense', 'buff', '-replace']}]}
        }
    }
    LIGHT_S3P2 = {
        'sword': {
            'startup': 0.1, 'recovery': 1.76667,
            'attr': [
                {'dmg': 1.984, 'dp': 100, 'iv': 0.63333},
                {'dmg': 1.984, 'iv': 0.8},
                {'dmg': 1.984, 'iv': 0.93333},
                {'dmg': 1.984, 'iv': 1.06667},
                {'dmg': 1.984, 'iv': 1.23333},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.43333}
            ]
        },
        'blade': {
            'startup': 0.1, 'recovery': 2.2,
            'attr': [
                {'dmg': 1.704, 'dp': 100, 'iv': 0.33333},
                {'dmg': 1.704, 'iv': 0.63333},
                {'dmg': 1.704, 'iv': 0.8},
                {'dmg': 1.704, 'iv': 0.93333},
                {'dmg': 1.704, 'iv': 1.06667},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.43333}
            ]
        },
        'dagger': {
            'startup': 0.1, 'recovery': 2.43333,
            'attr': [
                {'dmg': 1.312, 'dp': 100, 'iv': 0.26667},
                {'dmg': 1.312, 'iv': 0.7},
                {'dmg': 1.312, 'iv': 1.1},
                {'dmg': 1.312, 'iv': 1.3},
                {'dmg': 1.312, 'iv': 1.6},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 2.2}
            ]
        },
        'axe': {
            'startup': 0.1, 'recovery': 2.1,
            'attr': [
                {'dmg': 2.26, 'dp': 100, 'iv': 0.66667},
                {'dmg': 2.26, 'iv': 0.9},
                {'dmg': 2.26, 'iv': 1.2},
                {'dmg': 2.26, 'iv': 1.43333},
                {'dmg': 2.26, 'iv': 1.5},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.56667}
            ]
        },
        'lance': {
            'startup': 0.1, 'recovery': 3.23333,
            'attr': [
                {'dmg': 1.656, 'dp': 100, 'iv': 0.86667},
                {'dmg': 1.656, 'iv': 0.96667},
                {'dmg': 1.656, 'iv': 1.9},
                {'dmg': 1.656, 'iv': 2.0},
                {'dmg': 1.656, 'iv': 2.1},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 2.5}
            ]
        },
        'bow': {
            'startup': 0.1, 'recovery': 2.0,
            'attr': [
                {'dmg': 1.898, 'dp': 100, 'iv': 0.66667, 'msl': 1},
                {'dmg': 1.898, 'iv': 0.8, 'msl': 1},
                {'dmg': 1.898, 'iv': 0.9, 'msl': 1},
                {'dmg': 1.898, 'iv': 1.5, 'msl': 1},
                {'dmg': 1.898, 'iv': 1.53333, 'msl': 1},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.53333}
            ]
        },
        'wand': {
            'startup': 0.1, 'recovery': 1.66667,
            'attr': [
                {'dmg': 2.168, 'dp': 100, 'iv': 0.96667},
                {'dmg': 2.168, 'iv': 1.06667},
                {'dmg': 2.168, 'iv': 1.13333},
                {'dmg': 2.168, 'iv': 1.26667},
                {'dmg': 2.168, 'iv': 1.26667},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.36667}
            ]
        },
        'staff': {
            'startup': 0.1, 'recovery': 1.4,
            'attr': [
                {'dmg': 1.51, 'dp': 100, 'iv': 0.83333},
                {'dmg': 1.51, 'iv': 1.0},
                {'dmg': 1.51, 'iv': 1.16667},
                {'dmg': 1.51, 'iv': 1.33333},
                {'dmg': 1.51, 'iv': 1.36667},
                {'buff': ['self', 0.1, -1, 'sp', 'passive', '-replace'], 'iv': 1.36667}
            ]
        }
    }
    def __init__(self, conf, c):
        super().__init__(conf, c)

    def oninit(self, adv):
        pass

    @property
    def s3(self):
        if self.c.ele == 'light':
            return {**WeaponBase.AGITO_S3[self.c.ele], 's3_phase2': WeaponBase.LIGHT_S3P2[self.c.wt]}
        else:
            return WeaponBase.AGITO_S3[self.c.ele]


class AmuletPair:
    AB_LIMITS = {
        'a': 0.20, 's': 0.40, 'cc': 0.15, 'cd': 0.25,
        'fs': 0.50, 'bt': 0.30, 'sp': 0.15, 'bk': 0.30,
        'od': 0.15, 'lo_att': 0.60, 'ro_att': 0.10,
        'bc_att': 0.15, 'bc_cd': 0.15, 'bc_energy': 1, 'bc_regen': 3,
        'prep': 100, 'dc': 3, 'dcs': 3, 'da': 0.18, 'dt': 0.20,
        'k_burn': 0.30, 'k_poison': 0.25, 'k_paralysis': 0.25,
        'k_frostbite': 0.25, 'k_stun': 0.25, 'k_sleep': 0.25
    }
    def __init__(self, confs, c):
        self.a1 = AmuletBase(confs[0], c)
        self.a2 = AmuletBase(confs[1], c)
        self.c = c

    def __str__(self):
        return f'{self.a1}+{self.a2}'

    @property
    def att(self):
        return self.a1.att + self.a2.att

    @property
    def hp(self):
        return self.a1.hp + self.a2.hp

    @staticmethod
    def sort_ab(a):
        if len(a) <= 2:
            return -10 * a[1]
        if 'hp' not in a[2]:
            return -5 * a[1]
        return a[1]

    @property
    def ab(self):
        merged_ab = []

        limits = AmuletPair.AB_LIMITS.copy()
        sorted_ab = defaultdict(lambda: [])
        spf_ab = []
        for a in chain(self.a1.ab, self.a2.ab):
            if a[0] in limits:
                sorted_ab[a[0]].append(a)
            elif a[0] == 'spf':
                spf_ab.append(a)
            else:
                merged_ab.append(a)

        for cat, lst in sorted_ab.items():
            for a in sorted(lst, key=AmuletPair.sort_ab):
                delta = min(limits[cat], a[1])
                limits[cat] -= delta
                merged_ab.append((cat, delta, *a[2:]))
                if limits[cat] == 0:
                    break

        if spf_ab and limits['sp'] > 0:
            for ab in sorted(spf_ab, key=AmuletPair.sort_ab):
                delta = min(limits['sp'], a[1])
                limits['sp'] -= delta
                merged_ab.append(('spf', delta, *a[2:]))
                if limits['sp'] == 0:
                    break

        return merged_ab


class AmuletBase(EquipBase):
    AUGMENTS = 100
    def __init__(self, conf, c):
        super().__init__(conf, c)


class Slots:
    DRAGON_DICTS = subclass_dict(DragonBase)

    DEFAULT_DRAGON = {
        'flame': 'Gala_Mars',
        'water': 'Gaibhne_and_Creidhne',
        'wind': 'Vayu',
        'light': 'Gala_Thor',
        'shadow': 'Gala_Cat_Sith'
    }

    DEFAULT_WYRMPRINT = {
        'sword': ('The_Shining_Overlord', 'Primal_Crisis'),
        'blade': ('Resounding_Rendition', 'Breakfast_at_Valerios'),
        'dagger': ('Twinfold_Bonds', {
            'water': 'The_Prince_of_Dragonyule',
            'shadow': 'Howling_to_the_Heavens',
            'all': 'Levins_Champion'
        }),
        'axe': ('Kung_Fu_Masters', 'Breakfast_at_Valerios'),
        'lance': ('Resounding_Rendition', 'Breakfast_at_Valerios'),
        'wand': ('Candy_Couriers', 'Primal_Crisis'),
        'bow': ('Forest_Bonds', 'Primal_Crisis'),
        'staff': ('Resounding_Rendition', 'Breakfast_at_Valerios')
    }

    AFFLICT_WYRMPRINT = {
        'flame': 'Me_and_My_Bestie',
        'water': 'His_Clever_Brother',
        'wind': 'The_Fires_of_Hate',
        'light': 'Spirit_of_the_Season',
        'shadow': 'The_Fires_of_Hate'
    }

    def __init__(self, conf, sim_afflict=None):
        self.c = CharaBase(conf)
        self.sim_afflict = sim_afflict
        self.d = None
        self.w = None
        self.a = None

    def __str__(self):
        return ','.join([
            self.c.name, self.c.icon,
            self.c.ele, self.c.wt, str(round(self.att)),
            self.a.a1.name, self.a.a1.icon,
            self.a.a2.name, self.a.a2.icon,
            self.d.name, self.d.icon,
            self.w.name, self.w.icon,
        ])

    def set_d(self, key=None):
        drg = load_drg_json(self.c.ele)
        if not key:
            key = Slots.DEFAULT_DRAGON[self.c.ele]
        conf = Conf(drg[key])
        try:
            self.d = Slots.DRAGON_DICTS[key](conf, self.c)
        except KeyError:
            self.d = DragonBase(conf, self.c)

    def set_w(self, key=None):
        conf = Conf(weapons[self.c.ele][self.c.wt])
        self.w = WeaponBase(conf, self.c)

    def set_a(self, keys=None):
        if not keys:
            keys = list(Slots.DEFAULT_WYRMPRINT[self.c.wt])
            try:
                keys[1] = keys[1][self.c.ele]
            except KeyError:
                keys[1] = keys[1]['all']
            except TypeError:
                pass
            if self.sim_afflict:
                keys[1] = Slots.AFFLICT_WYRMPRINT[self.c.ele]
        confs = [Conf(wyrmprints[k]) for k in keys]
        self.a = AmuletPair(confs, self.c)

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
        pass


if __name__ == '__main__':
    from conf import load_adv_json
    conf = Conf(load_adv_json('Gala_Luca'))
    # conf['slots.a'] = ['Candy_Couriers', 'Me_and_My_Bestie']
    # conf['slots.d'] = 'Gala_Mars'
    slots = Slots(conf.c, True)
    slots.set_slots(conf.slots)
    print(slots.w.s3)
