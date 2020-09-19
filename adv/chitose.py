from core.advbase import *

def module():
    return Chitose

class Chitose(Adv):
    conf = {}
    conf['slots.a'] = ['Proper_Maintenance', 'From_Whence_He_Comes']
    conf['slots.paralysis.a'] = conf['slots.a']
    conf['slots.d'] = 'Tie_Shan_Gongzhu'
    conf['acl'] = """
        `s1
        `s4, s=1
        `s3, cancel and x!=1
        """
    conf['coabs'] = ['Tobias','Dagger2','Bow']
    conf['share'] = ['Summer_Luca','Summer_Cleo']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)