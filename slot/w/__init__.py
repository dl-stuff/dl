agito_buffs = {
    'flame': [
        {
        'buff'     : [('self',0.10,-1,'att','buff'), ('self',0.03,-1,'regen')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        {
        'buff'     : [('self',0.20,-1,'att','buff'), ('self',0.05,-1,'regen')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        { # combo time
        'buff'     : [('self',0.20,-1,'att','buff'), ('self',0.05,-1,'regen')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
    ],
    'wind': [
        {
        'buff'     : [('self',0.15,-1,'att','buff'), ('self',0.40,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        {
        'buff'     : [('self',0.25,-1,'att','buff'), ('self',0.50,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
    ],
    'shadow': [
        {
        'buff'     : [('spd',0.20,-1), ('self',0.30,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        {
        'buff'     : [('spd',0.30,-1), ('self',0.40,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        {
        'buff'     : [[('spd',0.30,-1), ('self',0.05,-1,'crit','chance')], ('self',0.40,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
    ],
    'water': [
        {
        'buff'     : [('self',0.8,-1,'crit','chance'), ('self',0.25,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        {
        'buff'     : [('self',0.12,-1,'crit','chance'), ('self',0.35,-1,'defense')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
    ],
    'light': [
        {
        'buff'     : [('self',0.10,-1,'att','buff'), ('self',0.07,-1,'sp')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        },
        {
        'buff'     : [('self',0.20,-1,'att','buff'), ('self',0.10,-1,'sp')],
        'sp'       : 3000,
        'startup'  : 0.25,
        'recovery' : 0.90,
        }
    ]
}

from slot import *

class LightAgitoWeaponBase(WeaponBase):
    ele = ['light']
    s3 = agito_buffs['light'][1]
    s3_dmg = 0.0

    def s3_before(self, adv, e):
        if not adv.s3_buff:
            return
        if adv.s3_buff.mod_type == 'att':
            adv.dmg_make(e.name, self.s3a['dmg'])
            adv.add_hits(5)
            adv.dragonform.charge_gauge(100)

    def s3_proc(self, adv, e):
        if not adv.s3_buff:
            return
        if adv.s3_buff.mod_type == 'att':
            self.a_s3 = adv.s3.ac
            try:
                adv.s3.ac = self.a_s3a
            except AttributeError:
                from core.advbase import S
                self.a_s3a = S('s3', Conf(self.s3a))
        elif adv.s3_buff.mod_type == 'sp':
            adv.s3.ac = self.a_s3

from slot.w.sword import *
from slot.w.blade import *
from slot.w.axe import *
from slot.w.dagger import *
from slot.w.lance import *
from slot.w.bow import *
from slot.w.wand import *
from slot.w.staff import *