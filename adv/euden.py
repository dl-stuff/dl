from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Euden

class Euden(Adv):    
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Me_and_My_Bestie()
    conf['slots.d'] = Gala_Mars()
    conf['acl'] = """
        `dragon(c3-s-s-end)
        `s3, not buff(s3)
        `s1
        `s2, fsc
        `s4, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Blade', 'Wand', 'Yuya']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)