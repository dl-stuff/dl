from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Zace

class Zace(Adv):
    a1 = ('s',0.2)
    conf = {}
    conf['slots.a'] = Dragon_and_Tamer()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), fsc
        `s3, not buff(s3)
        `s4
        `s1, cancel
        `s2, x>=3
        `fs, x=5
    """
    conf['coabs'] = ['Ieyasu','Wand','Bow']
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
