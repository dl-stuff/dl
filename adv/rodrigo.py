from core.advbase import *

def module():
    return Rodrigo

class Rodrigo(Adv):
    a1 = ('a',0.08,'hp70')
    conf = {}
    conf['acl'] = """
        `dragon.act('c3 s end')
        `s3, not this.s3_buff
        `s1
        `s2, fsc
        `fs, seq=3 and cancel
        """
if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
