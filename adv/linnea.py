from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Linnea


conf_alt_fs = {
    'fs1': {
        "attr": [{"dmg": 5.17, "sp": 600}, {"dmg": 5.17}, 3],
        'charge': 30 / 60.0,
        'startup': 16 / 60.0,
        'recovery': 34 / 60.0
    },
    'fs2': {
        "attr": [{"dmg": 2.87, "sp": 925}, {"dmg": 2.87}, 6],
        'charge': 108 / 60.0,
        'startup': 16 / 60.0,
        'recovery': 34 / 60.0
    },
    'fs3': {
        # 'dmg': 2124 / 100.0,
        "attr": [{"dmg": 2.36, "killer": [0.2, ["poison"]], "sp": 1500}, {"dmg": 2.36, "killer": [0.2, ["poison"]]}, 9],
        'charge': 210 / 60.0,
        'startup': 16 / 60.0,
        'recovery': 34 / 60.0
    }
}
class Linnea(Adv):
    conf = conf_alt_fs.copy()
    conf['slots.a'] = The_Lurker_in_the_Woods()+Levins_Champion()
    conf['slots.d'] = Fatalis()
    conf['acl'] = """
        `s4
        `s3
        `s2
        `s1
        `fs3
        """
    conf['coabs'] = ['Dagger', 'Grace', 'Axe2']
    conf['share'] = ['Hunter_Sarisse', 'Elisanne']

    def prerun(self):
        self.fs_hits = 0
        self.fs_ahits = 0
        self.fs_alt = FSAltBuff(uses=1)

    def s1_proc(self, e):
        self.fs_alt.on()

    def fs_before(self, e):
        if e.level > 0:
            self.hit_before = self.hits

    def fs_proc(self, e):
        if e.level > 0:
            self.update_fs_hits(self.hits-self.hit_before)

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
    test_with_argv(None, *sys.argv)