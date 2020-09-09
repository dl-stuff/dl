from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Zhu_Bajie

fs_damage = {
    'fs1': 2.07,
    'fs2': 2.97,
    'fs3': 3.83
}

conf_alt_fs = {
    'fs1': {
        'dmg': 0,
        'sp': 600,
        'charge': 24 / 60.0,
        'startup': 20 / 60.0,
        'recovery': 20 / 60.0,
        'hit': -1,
    },
    'fs2': {
        'dmg': 0,
        'sp': 960,
        'charge': 48 / 60.0,
        'startup': 20 / 60.0,
        'recovery': 20 / 60.0,
        'hit': -1,
    },
    'fs3': {
        'dmg': 0,
        'sp': 1400,
        'charge': 72 / 60.0,
        'startup': 20 / 60.0,
        'recovery': 20 / 60.0,
        'hit': -1,
    }
}

class Zhu_Bajie(Adv):
    conf = conf_alt_fs.copy()
    conf['slots.a'] = Mega_Friends()+The_Plaguebringer()
    conf['slots.paralysis.a'] = Mega_Friends()+Spirit_of_the_Season()
    conf['acl'] = """
        `dragon
        `s3, fsc and not buff(s3)
        `s2, fsc
        `s1, fsc
        `s4, fsc
        `dodge, fsc
        `fs3
        """
    conf['coabs'] = ['Blade', 'Lucretia', 'Peony']
    conf['share'] = ['Summer_Patia']


    def fs_proc(self, e):
        with KillerModifier(e.name, 'hit', 0.5, ['paralysis']):
            self.dmg_make(e.base, fs_damage[e.base])

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
