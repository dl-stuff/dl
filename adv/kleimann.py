from core.advbase import *

def module():
    return Kleimann

class Kleimann(Adv):
    a1 = ('fs',0.4)
    a3 = ('s',0.2)
 
    conf = {}
    conf['acl'] = """
        `dragon
        `s3, not this.s3_buff
        `s1
        `s2
        """

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
