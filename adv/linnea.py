from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Linnea


class Linnea(Adv):
    conf = {}
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
        for lv in range(1, 4):
            for h in range(3, lv*3+1, 3):
                setattr(self, f'fs{lv}_enhanced_hit{h}', self.a1_fs_prep)

    def a1_fs_prep(self, name, base, group, aseq):
        self.charge_p(base, 0.30, target='s1')


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)