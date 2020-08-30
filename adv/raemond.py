from core.advbase import *

def module():
    return Raemond

class Raemond(Adv):
    a1 = ('lo_defense', 0.50)

    conf = {}
    conf['acl'] = """
        `dragon
        `s4
        `s1
        `s2, fsc
        `s3, fsc
        `fs, x=2
        """
    coab = ['Cleo','Lucretia','Peony']
    share = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
