from core.advbase import *

def module():
    return Orion

class Orion(Adv):
    a1 = ('cc',0.10,'hit15')
    a3 = ('prep', 0.50)
    conf = {}
    conf['acl'] = """
        `dragon
        `s3, not this.s3_buff
        `s1
        `s2
        `fs, x=4
    """

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
