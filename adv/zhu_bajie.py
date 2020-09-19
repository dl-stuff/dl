from core.advbase import *

def module():
    return Zhu_Bajie

class Zhu_Bajie(Adv):
    conf = {}
    conf['slots.a'] = ['Mega_Friends', 'The_Plaguebringer']
    conf['slots.paralysis.a'] = ['Mega_Friends', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon
        `s3, fsc and not buff(s3)
        `s2, fsc
        `s1, fsc
        `s4, fsc
        `dodge, fsc
        `fs3
        """
    conf['coabs'] = ['Blade', 'Lucretia', 'Peony']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
