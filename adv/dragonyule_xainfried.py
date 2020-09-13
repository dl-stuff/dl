from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Dragonyule_Xainfried

class Dragonyule_Xainfried(Adv):
    comment = 'no s2'

    conf = {}
    conf['slots.a'] = A_Dogs_Day()+Castle_Cheer_Corps()
    conf['slots.poison.a'] = conf['slots.a']
    conf['slots.d'] = Freyja()
    conf['acl'] = """
        `s4
        `s1
        `s3, x>2 or fscf
        `fs,x=5
        `dodge,fscf
        """
    conf['coabs'] = ['Blade','Bow','Tobias']
    conf['share'] = ['Marty','Tobias']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

