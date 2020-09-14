from core.advbase import *
from slot.a import *

def module():
    return Halloween_Edward

class Halloween_Edward(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Red_Impulse()
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