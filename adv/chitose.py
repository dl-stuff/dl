from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Chitose

class Chitose(Adv):
    conf = {}
    conf['slots.a'] = A_Game_of_Cat_and_Boar()+Castle_Cheer_Corps()
    conf['slots.paralysis.a'] = conf['slots.a']
    conf['slots.d'] = Tie_Shan_Gongzhu()
    conf['acl'] = """
        `s1
        `s4, s=1
        `s3, x>2
        `fs, x=5
        `dodge,fscf
        """
    conf['coabs'] = ['Tobias','Dagger2','Bow']
    conf['share'] = ['Summer_Luca','Summer_Cleo']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)