from core.advbase import *

def module():
    return Mordecai

class Mordecai(Adv):
    conf = {}
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s1
        `s2
        `s4, x=5
        """
    conf['coabs'] = ['Halloween_Elisanne','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)