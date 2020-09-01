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
    s3a = {}

    def setup(self, c, adv):
        super(LightAgitoWeaponBase, self).setup(c, adv)
        if (self.onele or 'all' in self.ele) and adv is not None and adv.s3.owner is None:
            adv.rebind_function(LightAgitoWeaponBase, 's3_before', 's3_before')
            adv.rebind_function(LightAgitoWeaponBase, 's3_proc', 's3_proc')
            adv.s3a = self.s3a

    def s3_before(self, e):
        if not self.s3_buff:
            return
        if self.s3_buff.mod_type == 'att':
            self.dmg_make(e.name, self.s3a['dmg'])
            self.add_hits(5)
            self.dragonform.charge_gauge(100)

    def s3_proc(self, e):
        if not self.s3_buff:
            return
        if self.s3_buff.mod_type == 'att':
            self.a_s3 = self.s3.ac
            try:
                self.s3.ac = self.a_s3a
            except AttributeError:
                from core.advbase import S
                self.a_s3a = S('s3', Conf(self.s3a))
        elif self.s3_buff.mod_type == 'sp':
            self.s3.ac = self.a_s3

from slot.w.sword import *
from slot.w.blade import *
from slot.w.axe import *
from slot.w.dagger import *
from slot.w.lance import *
from slot.w.bow import *
from slot.w.wand import *
from slot.w.staff import *