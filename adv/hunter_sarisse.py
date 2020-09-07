from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Hunter_Sarisse

startups = {
    'startup': 4 / 60,
    'fs1.startup': 94 / 60,
    'fs2.startup': 94 / 60,
    'fs3.startup': 94 / 60,
    'fs4.startup': 94 / 60,
    'x1.startup': 7 / 60,
    'dodge.startup': 18 / 60,
    'recovery': 59 / 60,
}

fs_damage = {
    'fs1': 0.74,
    'fs2': 0.84,
    'fs3': 0.94,
    'fs4': 1.29
}

sarisse_derp = {
    'fs1': {
        **startups,
        'dmg': 0.0,
        'sp': 500,
        'charge': 30 / 60.0,
        'recovery': 4 / 60.0,
        'hit': 3,
    },
    'fs2': {
        **startups,
        'dmg': 0.0,
        'sp': 710,
        'charge': (30+42) / 60.0,
        'hit': 3,
    },
    'fs3': {
        **startups,
        'dmg': 0.0,
        'sp': 920,
        'charge': (30+42*2) / 60.0,
        'hit': 4,
    },
    'fs4': {
        **startups,
        'dmg': 0.0,
        'sp': 1140,
        'charge': (30+42*3) / 60.0,
        'hit': 4,
    }
}

class Hunter_Sarisse(Adv):
    comment = '4hit FS on A&O sized enemy (see special for 20hit); needs combo time to keep combo'

    conf = sarisse_derp.copy()
    conf['slots.a'] = The_Lurker_in_the_Woods()+Primal_Crisis()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `s3, fsc
        `s1, fsc
        `s2, fsc
        `s4, fsc
        `dodge, fsc
        `fs4
    """
    conf['coabs'] = ['Dagger', 'Xander', 'Grace']
    conf['share'] = ['Gala_Elisanne', 'Eugene']

    def prerun(self):
        self.fs_attdown = Debuff('fs', 0.15, 10, 1, 'attack')
        self.hsari_fs_boost = SingleActionBuff('s1', 1.00, 1, 'fs', 'buff')
        self.fs_attenuation = 1
        self.s2_cspd = Spdbuff(f's2_spd',0.30,30, mtype='cspd')

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.hsari_fs_boost = SingleActionBuff(dst, 1.00, 1, 'fs', 'buff')

    def fs_proc(self, e):
        self.fs_attdown.on()
        self.dmg_make(e.name, fs_damage[e.name]*self.conf[e.name].hit)
        for p in range(1, self.fs_attenuation):
            self.dmg_make(f'{e.name}_extra_{p}', fs_damage[e.name]*self.conf[e.name].hit, attenuation=(0.30, p))

    def s1_proc(self, e):
        self.hsari_fs_boost.on()

    def s2_proc(self, e):
        self.s2_cspd.on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
