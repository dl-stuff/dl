from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Melody

class Melody(Adv):
    conf = {}
    conf['slots.a'] = A_Dogs_Day()+From_Whence_He_Comes()
    conf['slots.d'] = Ariel()
    conf['acl'] = """
        `s3, not buff(s3)
        `s1
        `s4
        `fs, xf=5
    """
    conf['coabs'] = ['Bow','Tobias','Dagger2']
    conf['share'] = ['Dragonyule_Xainfried']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)