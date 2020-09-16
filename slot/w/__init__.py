agito_buffs = {
    'flame': [
        None, # add 0ub again 1day mayb
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': ['self', 0.20, -1, 'att', 'buff', '-replace']}]
            },
            's3_phase2': {
                'attr': [{'buff': ['self', 0.05, -1, 'regen', 'buff', '-replace']}]
            }
        },
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': [['self', 0.20, -1, 'att', 'buff'], ['self', 1.00, -1, 'ctime', 'passive'], '-replace']}]
            },
            's3_phase2': {
                'attr': [{'buff': ['self', 0.05, -1, 'regen', 'buff', '-replace']}]
            }
        },
    ],
    'wind': [
        None,
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': ['self', 0.25, -1, 'att', 'buff', '-replace']}]
            },
            's3_phase2': {
                'attr': [{'buff': ['self', 0.50, -1, 'defense', 'buff', '-replace']}]
            }
        },
    ],
    'shadow': [
        None,
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': ['spd', 0.30, -1, '-replace']}]
            },
            's3_phase2': {
                'attr': [{'buff': ['self', 0.40, -1, 'defense', 'buff', '-replace']}]
            }
        },
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': [['spd', 0.30, -1], ['self', 0.05, -1, 'crit', 'chance'], '-replace']}]
            },
            's3_phase2': {
                'attr': [{'buff': ['self', 0.40, -1, 'defense', 'buff', '-replace']}]
            }
        },
    ],
    'water': [
        None,
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': ['self', 0.20, -1, 'crit', 'chance', '-replace']}]
            },
            's3_phase2': {
                'attr': [{'buff': ['self', 0.35, -1, 'defense', 'buff', '-replace']}]
            }
        },
    ],
    'light': [
        None,
        {
            's3': {
                'sp' : 3000,
                'startup' : 0.25,
                'recovery' : 0.90,
            },
            's3_phase1': {
                'attr': [{'buff': ['self', 0.20, -1, 'att', 'buff', '-replace']}]
            },
            's3_phase2': {
                'attr': [
                    {'buff': ['self', 0.10, -1, 'sp', 'passive', '-replace']},
                    {"dmg": 0, "dp": 100}
                ]
            }
        },
    ]
}

from slot import *

class LightAgitoWeaponBase(WeaponBase):
    ele = ['light']
    s3_base = agito_buffs['light'][1]
    s3a = {}

    def __init__(self):
        super().__init__()
        self.s3.s3_phase2.attr[0]['dmg'] = self.s3a['dmg']
        self.s3.s3_phase2.startup = self.s3a['startup']
        self.s3.s3_phase2.recovery = self.s3a['recovery']


    # # FIXME come bacc and fix this shit
    # s3a = {}

    # def setup(self, c, adv):
    #     super(LightAgitoWeaponBase, self).setup(c, adv)
    #     if adv is not None and adv.conf.s3.owner is None:
    #         adv.rebind_function(LightAgitoWeaponBase, 's3_before', 's3_before')
    #         adv.rebind_function(LightAgitoWeaponBase, 's3_proc', 's3_proc')
    #         adv.s3a = self.s3a

    # def s3_before(self, e):
    #     if not buff(s3):
    #         return
    #     if self.s3_buff.mod_type == 'att':
    #         self.dmg_make(e.name, self.s3a['dmg'])
    #         self.add_hits(5)
    #         self.dragonform.charge_gauge(100)

    # def s3_proc(self, e):
    #     if not buff(s3):
    #         return
    #     if self.s3_buff.mod_type == 'att':
    #         self.a_s3 = self.s3.ac
    #         try:
    #             self.s3.ac = self.a_s3a
    #         except AttributeError:
    #             from core.advbase import S
    #             self.a_s3a = S('s3', Conf(self.s3a))
    #     elif self.s3_buff.mod_type == 'sp':
    #         self.s3.ac = self.a_s3

from slot.w.sword import *
from slot.w.blade import *
from slot.w.axe import *
from slot.w.dagger import *
from slot.w.lance import *
from slot.w.bow import *
from slot.w.wand import *
from slot.w.staff import *