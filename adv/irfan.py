from core.advbase import *

def module():
    return Irfan

class Irfan(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'The_Red_Impulse']
    conf['acl'] = """
        `dragon
        `s3
        `s4
        `s1
        `s2, x>3 or fsc
        `fs, x=5
        """
    conf['coabs'] = ['Cleo','Raemond','Peony']
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)