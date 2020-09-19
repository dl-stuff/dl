from core.advbase import *
from module.bleed import Bleed, mBleed
from module.x_alt import X_alt

def module():
    return Mega_Man


class Skill_Ammo(Skill):
    def __init__(self, name=None, acts=None):
        super().__init__(name, acts)
        self.c_ammo = 0

    @property
    def ammo(self):
        return self.ac.conf.ammo

    @property
    def cost(self):
        return self.ac.conf.cost
    
    def check(self):
        if self._static.silence == 1:
            return False
        return self.c_ammo >= self.cost

    def check_full(self):
        if self._static.silence == 1:
            return False
        return self.c_ammo >= self.ammo

    def charge_ammo(self, ammo):
        self.c_ammo = min(self.ammo, self.c_ammo + ammo)

class Mega_Man(Adv):
    comment = '16 hits leaf shield (max 32 hits)'

    conf = {}
    conf['slots.d'] = 'Gala_Mars'
    conf['slots.a'] = ['Primal_Crisis', 'Levins_Champion']
    conf['acl'] = """
        `dragon, s=4
        `s3, not buff(s3)
        `s4
        if bleed.get() >= 3
        `s2, c_x(metalblade) or c_x(default)
        `s1, c_x(metalblade)
        else
        `s1, c_x(default) and s1.check_full()
        end
    """
    conf['coabs'] = ['Blade', 'Marth', 'Dagger2']
    conf['share'] = ['Karl']

    conf['dragonform'] = {
        'act': 'c5-s',

        'dx1.dmg': 1.20,
        'dx1.startup': 10 / 60.0, # c1 frames
        'dx1.hit': 3,

        'dx2.dmg': 1.20,
        'dx2.startup': 13 / 60.0, # c2 frames
        'dx2.hit': 3,

        'dx3.dmg': 1.20,
        'dx3.startup': 14 / 60.0, # c3 frames
        'dx3.hit': 3,

        'dx4.dmg': 1.20,
        'dx4.startup': 14 / 60.0, # c4 frames
        'dx4.hit': 3,

        'dx5.dmg': 1.20,
        'dx5.startup': 14 / 60.0, # c5 frames
        'dx5.recovery': 23 / 60.0, # recovery
        'dx5.hit': 3,

        'ds.dmg': 6.00,
        'ds.recovery': 113 / 60, # skill frames
        'ds.hit': 5,

        'dodge.startup': 45 / 60.0, # dodge frames
    }
    def ds_proc(self):
        return self.dmg_make('ds',self.dragonform.conf.ds.dmg,'s')

    def __init__(self, conf=None, cond=None):
        super().__init__(conf=conf, cond=cond)
        self.a_s_dict['s1'] = Skill_Ammo('s1')
        self.a_s_dict['s2'] = Skill_Ammo('s2')
        self.bleed = Bleed('g_bleed',0).reset()

    def prerun(self):
        self.s1.charge_ammo(2000)
        self.s2.charge_ammo(4000)

    @property
    def skills(self):
        return self.s3, self.s4

    def hitattr_make(self, name, base, group, aseq, attr, onhit):
        ammo = attr.get('ammo', 0)
        if ammo > 0:
            for s in (self.s1, self.s2):
                s.charge_ammo(ammo)
        elif ammo < 0:
            s = self.s1 if group == 'metalblade' else self.s2
            s.charge_ammo(ammo)
            if s.c_ammo <= 0:
                self.current_x = 'default'
        if ammo != 0:
            log('ammo', name, ammo, ' '.join(f'{s.c_ammo}/{s.ammo}' for s in (self.s1, self.s2)))
        super().hitattr_make(name, base, group, aseq, attr, onhit)

    def s1_proc(self, e):
        if self.current_x != 'metalblade':
            self.current_x = 'metalblade'
        else:
            self.current_x = 'default'

    def s2_proc(self, e):
        if self.current_x != 'leafshield':
            self.current_x = 'leafshield'
        else:
            self.current_x = 'default'

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)