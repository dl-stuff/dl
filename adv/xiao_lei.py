from core.advbase import *

def module():
    return Xiao_Lei

class Xiao_Lei(Adv):
    conf = {}
    conf['acl'] = """
        `dragon
        `s2
        `s1, cancel
        `s3
        `s4, x=5
        """
    conf['coabs'] = ['Blade','Halloween_Elisanne','Peony']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)