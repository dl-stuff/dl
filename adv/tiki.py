from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import X_alt


def module():
    return Tiki


# divine dragon mods
tiki_conf = {    
    'x1.dmg': 7 / 100.0,
    'x1.sp': 88,
    'x1.utp': 2,
    'x1.startup': 12 / 60.0,
    'x1.recovery': 0,
    'x1.hit': 1,

    'x2.dmg': 15 / 100.0,
    'x2.sp': 141,
    'x2.utp': 3,
    'x2.startup': 22 / 60.0,
    'x2.recovery': 0,
    'x2.hit': 1,

    'x3.dmg': 11 / 100.0,
    'x3.sp': 178,
    'x3.utp': 4,
    'x3.startup': 36 / 60.0,
    'x3.recovery': 0 / 60.0,
    'x3.hit': 1,

    'x4.dmg': 31 / 100.0,
    'x4.sp': 350,
    'x4.utp': 5,
    'x4.startup': 26 / 60.0,
    'x4.recovery': 0 / 60.0,
    'x4.hit': 1,

    'x5.dmg': 33 / 100.0,
    'x5.sp': 367,
    'x5.utp': 6,
    'x5.startup': 20 / 60.0,
    'x5.recovery': 0 / 60.0,
    'x5.hit': 1,

    'dodge.startup': 40 / 60.0,  # actually dragon dodge but w/e

    'x1_divine.dmg': 211 / 100.0,
    'x1_divine.sp': 290,
    'x1_divine.startup': 20 / 60.0,
    'x1_divine.recovery': 0,
    'x1_divine.hit': 1,

    'x2_divine.dmg': 252 / 100.0,
    'x2_divine.sp': 350,
    'x2_divine.startup': 30 / 60.0,
    'x2_divine.recovery': 0,
    'x2_divine.hit': 1,

    'x3_divine.dmg': 358 / 100.0,
    'x3_divine.sp': 520,
    'x3_divine.startup': 49 / 60.0,
    'x3_divine.recovery': 67 / 60.0,
    'x3_divine.hit': 1,
}


class Tiki(Adv):
    comment = 'dragon damage does not work on divine dragon'

    conf = tiki_conf.copy()
    conf['slots.a'] = Twinfold_Bonds()+The_Prince_of_Dragonyule()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Dragonyule_Jeanne()
    conf['acl'] = """
        if divine_dragon.get()
        `s1
        `s2
        `dodge, x=3
        else
        `s3, not buff(s3) and fsc
        `dragon, dgauge>=1800
        `s4, x=5
        `s2
        `s1, fsc
        `fs,x=5
        end
    """
    conf['coabs'] = ['Blade', 'Xander', 'Catherine']
    conf['share'] = ['Kleimann']
    

    def d_slots(self):
        if self.duration <= 60:
            self.conf['slots.a'] = Twinfold_Bonds()+The_Chocolatiers()
            self.conf['slots.frostbite.a'] = self.conf['slots.a']

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            'divine',
            x=True, s1=True, s2=True
        ))

    def x_proc(self, e):
        try:
            self.dragonform.charge_gauge(self.conf[e.name].utp, utp=True)
        except:
            self.dragonform.charge_gauge(0, utp=True)

    def prerun(self):
        self.divine_dragon = self.dragonform.set_dragondrive(ModeManager(
            'divine',
            # buffs=[Selfbuff('divine_dragon', self.dragonform.ddamage(), -1, 'att', 'dragon')], # reeee
            x=True, s1=True, s2=True
        ), max_gauge=1800, shift_cost=560, drain=40)
        Event('dragon_end').listener(self.dragondrive_on)
        Event('dragondrive_end').listener(self.dragondrive_off)

    def dragondrive_on(self, e):
        self.a_fs_dict['fs'].set_enabled(False)
        self.s3.set_enabled(False)
        self.s4.set_enabled(False)
        self.charge_p('divine_dragon', 100)

    def dragondrive_off(self, e):
        self.a_fs_dict['fs'].set_enabled(True)
        self.s3.set_enabled(True)
        self.s4.set_enabled(True)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
