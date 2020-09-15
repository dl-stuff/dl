from core.advbase import *

def module():
    return Malka

class Malka(Adv):
    conf = {}
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2
        `s4
        `s1, cancel
        `fs, seq=5
        """
    conf['coabs'] = ['Blade','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)