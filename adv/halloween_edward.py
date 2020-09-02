from core.advbase import *
from slot.a import *

def module():
    return Halloween_Edward

class Halloween_Edward(Adv):
    a1 = ('a',0.1,'hp100')

    conf = {}
    conf['slots.a'] = RR()+The_Red_Impulse()
    conf['acl'] = """
        `dragon
        `s3
        `s4, cancel
        `s1, cancel
        `s2, x=5
        """
    conf['coabs'] = ['Raemond','Cleo','Peony']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)