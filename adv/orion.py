from core.advbase import *
from slot.d import *

def module():
    return Orion

class Orion(Adv):
    a1 = ('cc',0.10,'hit15')
    a3 = ('prep', 0.50)
    conf = {}
    conf['acl'] = """
        `dragon(c3-s-end), self.sim_afflict or self.trickery <= 1
        `s3, not self.s3_buff
        `s4
        `s2, x=4 or x=5
        `s1, self.s3_buff and cancel
        `fs, x=5
    """
    conf['coabs'] = ['Ieyasu','Wand','Axe2']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['coabs'] = ['Ieyasu','Wand','Forte']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
