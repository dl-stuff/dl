from core.advbase import *

def module():
    return Vice

class Vice(Adv):
    a1 = ('bk',0.2)
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
