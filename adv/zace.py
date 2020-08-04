from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Zace

class Zace(Adv):
    a1 = ('s',0.2)
    conf = {}
    conf['slots.a'] = Dragon_and_Tamer()+Primal_Crisis()
    conf['acl'] = """
        `dragon.act('c3 s end'), fsc
        `s3, not self.s3_buff
        `s4
        `s1, cancel
        `s2, x>=3
        `fs, x=5
    """
    coab = ['Ieyasu','Wand','Bow']
    share = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
