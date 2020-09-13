from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Fritz

class Fritz(Adv):
    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+The_Red_Impulse()
    conf['acl'] = """
        `dragon
        `s3
        `s1
        `s4, cancel
        `s2, x=5
        `fs, x=5
        """
    conf['coabs'] = ['Cleo','Raemond','Peony']
    conf['share'] = ['Kleimann']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)