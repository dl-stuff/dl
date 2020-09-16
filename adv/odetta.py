from core.advbase import *

def module():
    return Odetta

class Odetta(Adv):
    conf = {}
    conf['acl'] = """
        `dragon
        `s4, cancel
        `s2, cancel
        `s3, fsc
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Cleo','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)