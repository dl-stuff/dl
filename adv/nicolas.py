from core.advbase import *

def module():
    return Nicolas

class Nicolas(Adv):
    conf = {}
    conf['acl'] = """
        `dragon.act("c3 s end"),s4.check()
        `s3, not self.s3_buff
        `s4
        `s2
        `s1, x>2
        """
    coab = ['Blade','Akasha','Lin_You']
    share = ['Curran']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)

