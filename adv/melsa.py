from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Melsa

class Melsa(Adv):
    a3 = ('cc',0.08,'hit15')

    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+Levins_Champion()
    conf['acl'] = """
        `dragon,s
        `s3, not self.s3_buff and x=5
        `s4
        `s1, cancel
        `s2,s=1
        `fs, x=5
    """
    coab = ['Blade', 'Wand', 'Marth']
    share = ['Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
