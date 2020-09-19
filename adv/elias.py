from core.advbase import *

def module():
    return Elias

class Elias(Adv):
    conf = {}
    conf['slots.paralysis.a'] = ['Forest_Bonds', 'The_Red_Impulse']
    conf['acl'] = """
        `dragon
        `s3
        `s4
        `s1
        `s2, fsc and not self.energy()=5
        `fs, x=3
        """
    conf['coabs'] = ['Cleo','Raemond','Peony']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)