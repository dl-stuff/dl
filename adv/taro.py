from core.advbase import *

def module():
    return Taro

class Taro(Adv):
    conf = {}
    conf['acl'] = """
        `dragon, x=5
        `s3, not this.s3_buff
        `s1, x=5
        `s2, x=5
        """

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
