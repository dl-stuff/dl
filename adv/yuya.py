from core.advbase import *
from slot.a import *

def module():
    return Yuya

class Yuya(Adv):    
    conf = {}
    conf['slots.burn.a'] = Twinfold_Bonds()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon, s=1
        `s3, not buff(s3)
        `s4
        `s1
        `fs, x=4
        """
    conf['coabs'] = ['Blade', 'Marth', 'Dagger2']
    conf['share'] = ['Gala_Mym']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
