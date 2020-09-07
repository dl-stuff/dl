from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Linnea


conf_alt_fs = {
    'fs1': {
        'dmg': 1551 / 100.0,
        'sp': 600,
        'charge': 30 / 60.0,
        'startup': 16 / 60.0,
        'recovery': 34 / 60.0,
        'hit': 3
    },
    'fs2': {
        'dmg': 1722 / 100.0,
        'sp': 925,
        'charge': 108 / 60.0,
        'startup': 16 / 60.0,
        'recovery': 34 / 60.0,
        'hit': 6
    },
    'fs3': {
        # 'dmg': 2124 / 100.0,
        'dmg': 0,
        'sp': 1500,
        'charge': 210 / 60.0,
        'startup': 16 / 60.0,
        'recovery': 34 / 60.0,
        'hit': 9
    }
}
class Linnea(Adv):
    comment = 'Gala Leif > Yaten if -Def% debuff. Axe2 > Yaten if +Str% buff'
    conf = conf_alt_fs.copy()

    conf['slots.a'] = The_Lurker_in_the_Woods()+Seaside_Princess()
    conf['slots.d'] = Fatalis()
    conf['acl'] = """
        `s3, not self.s3_buff
        `s4
        `s2
        `s1
        `fs3
        """
    conf['coabs'] = ['Delphi', 'Grace', 'Yaten']
    conf['share'] = ['Hunter_Sarisse']
    def prerun(self):
        self.fs_hits = 0
        self.fs_ahits = 0
        self.fs_alt = FSAltBuff(self, uses=1)

        self.s2_cspd = Spdbuff('s2_spd',0.3,15, mtype='cspd')
        self.s2_mode = 0
        self.a_s2 = self.s2.ac
        self.a_s2a = S('s2', Conf({'startup': 0.10, 'recovery': 1.3333}))

    def s1_proc(self, e):
        self.fs_alt.on()

    def s2_proc(self, e):
        if self.s2_mode == 0:
            self.s2_cspd.on()
            self.s2.ac = self.a_s2a
        else:
            self.dmg_make(e.name, 14.20)
            self.add_hits(3)
            self.s2.ac = self.a_s2
        self.s2_mode = (self.s2_mode + 1) % 2


    def fs_proc(self, e):
        if e.level == 3:
            with KillerModifier('fs_killer', 'hit', 0.2, ['poison']):
                self.dmg_make(e.name, 21.24, 'fs')
        self.update_fs_hits(self.conf[e.name+'.hit'])

    def update_fs_hits(self, fs_hits):
        self.fs_hits += fs_hits
        if self.fs_hits // 3 > self.fs_ahits:
            delta = self.fs_hits // 3 - self.fs_ahits
            self.fs_ahits = self.fs_hits // 3
            self.s1.charge(self.sp_convert(0.30*delta, self.conf.s1.sp))
        # fs always break combo
        self.hits = 0


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)