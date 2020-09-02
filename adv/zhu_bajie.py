from core.advbase import *
from slot.a import *
from slot.d import *
from module.x_alt import Fs_alt

def module():
    return Zhu_Bajie


class Zhu_Bajie(Adv):
    a3 = ('ro', 0.10)

    conf = {}
    conf['slots.a'] = Mega_Friends()+The_Plaguebringer()
    conf['slots.paralysis.a'] = Mega_Friends()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3, fsc and not self.s3_buff
        `s2, fsc
        `s1, fsc
        `s4, fsc
        `dodge, fsc
        `fs3
        """
    conf['coabs'] = ['Blade', 'Lucretia', 'Peony']
    conf['share'] = ['Summer_Patia']

    def prerun(self):
        self.conf.fs.hit = 1
        conf_alt_fs = {
            'fs1': {
                'dmg': 207 / 100.0,
                'sp': 600,
                'charge': 24 / 60.0,
                'startup': 20 / 60.0,
                'recovery': 20 / 60.0,
            },
            'fs2': {
                'dmg': 297 / 100.0,
                'sp': 960,
                'charge': 48 / 60.0,
                'startup': 20 / 60.0,
                'recovery': 20 / 60.0,
            },
            'fs3': {
                'dmg': 383 / 100.0,
                'sp': 1400,
                'charge': 72 / 60.0,
                'startup': 20 / 60.0,
                'recovery': 20 / 60.0,
            }
        }
        self.fs_alt = Fs_alt(self, conf_alt_fs, l_fs=self.l_melee_fs)
        self.fs_alt.on(-1)

    def l_melee_fs(self, e):
        log('cast', 'fs')
        self.fs_before(e)
        self.add_hits(-1)
        with KillerModifier(e.name, 'hit', 0.5, ['paralysis']):
            self.dmg_make('fs', self.conf[e.name+'.dmg'], 'fs')
        self.fs_proc(e)
        self.think_pin('fs')
        self.charge(e.name, self.conf[e.name+'.sp'])

    def s1_proc(self, e):
        with CrisisModifier(e.name, 1.15, self.hp):
            self.dmg_make(e.name, 8.52)
        self.afflics.stun(e.name, 110)

    def s2_proc(self, e):
        if self.hp > 30:
            self.set_hp(20)
        else:
            Selfbuff(e.name, 0.20, 10).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
