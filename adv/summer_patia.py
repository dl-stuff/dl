from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Summer_Patia

spatia_fs = {
    'fs1': {
        'dmg': 207 / 100.0,
        'sp': 600,
        'charge': 24 / 60.0,
        'startup': 24 / 60.0,
        'recovery': 46 / 60.0,
        'hit': -1,
    },
    'fs1_a': {
        'dmg': 287 / 100.0,
    },
    'fs2': {
        'dmg': 297 / 100.0,
        'sp': 900,
        'charge': 48 / 60.0,
        'startup': 24 / 60.0,
        'recovery': 46 / 60.0,
        'hit': -1,
    },
    'fs2_a': {
        'dmg': 412 / 100.0,
    },
    'fs3': {
        'dmg': 384 / 100.0,
        'sp': 1400,
        'charge': 72 / 60.0,
        'startup': 24 / 60.0,
        'recovery': 46 / 60.0,
        'hit': -1,
    },
    'fs3_a': {
        'dmg': 532 / 100.0,
    },
}

class Summer_Patia(Adv):
    comment = 'cannot build combo for Cat Sith; uses up 15 stacks by 46.94s'
    a3 = [('antiaffself_poison', 0.15, 10, 5), ('edge_poison', 60, 'hp50')]

    conf = spatia_fs.copy()
    conf['slots.poison.a'] = Kung_Fu_Masters()+The_Plaguebringer()
    conf['slots.d'] = Shinobi()
    conf['acl'] = """
        # use dragon if using Cat Sith
        # `dragon(c3-s-end), fsc
        `s3, not buff(s3)
        `s1, fsc
        `s2, fsc
        `s4, fsc
        `dodge, fsc
        `fs3
    """
    conf['coabs'] = ['Summer_Patia', 'Blade', 'Wand', 'Curran']
    conf['share'] = ['Curran']

    def prerun(self):
        self.fs_alt = FSAltBuff(group='a', uses=1)

    def d_slots(self):
        if self.duration <= 120:
            self.conf['slots.d'] = Gala_Cat_Sith()

    def s1_before(self, e):
        self.dmg_make(e.name, 7.47)

    def s1_proc(self, e):
        self.dmg_make(e.name, 7.47)
        self.fs_alt.on()

    def s2_proc(self, e):
        self.afflics.poison(e.name,120,0.582)

    def fs_proc(self, e):
        e.group and self.afflics.poison(e.name, 110, 0.436)


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)