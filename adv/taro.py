from core.advbase import *

def module():
    return Taro

class Taro(Adv):
    conf = {}
    conf['acl'] = """
        `dragon.act('c3 s end'),fsc
        `s3, not self.s3_buff
        `s4
        `s1,x=5
        `s2,x=5
        `fs,x=5 and self.s3_buff
        """
    coab = ['Wand','Dagger','Bow']
    share = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
