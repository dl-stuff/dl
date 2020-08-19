from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Rex

class Rex(Adv):
    conf = {}
    conf['slots.a'] = Summer_Paladyns()+Primal_Crisis()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end'), cancel
        `s3
        `s4
        `s1
        `s2, cancel
        `fs, cancel and s1.charged>=s1.sp-self.sp_val('fs')
    """
    coab = ['Blade', 'Xander', 'Summer_Estelle']
    share = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)