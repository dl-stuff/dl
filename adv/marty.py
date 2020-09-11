from core.advbase import *
from slot.d import *

def module():
    return Marty

class Marty(Adv):
    conf = {}
    conf['acl'] = """
        `dragon, s=4
        `s3, fsc and not buff(s3)
        `s2, fsc
        `s4, fsc
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Blade', 'Marth', 'Yuya']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)