from core.advbase import *

def module():
    return Marty

class Marty(Adv):
    a1 = ('sp',0.05)

    conf = {}
    conf['acl'] = """
        `dragon, s=4
        `s3, fsc and not buff(s3)
        `s4, fsc
        `s1, fsc
        `fs, x=3
        """
    conf['coabs'] = ['Blade', 'Marth', 'Yuya']
    conf['share'] = ['Summer_Patia']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)