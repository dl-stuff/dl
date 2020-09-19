from core.advbase import *

def module():
    return Valentines_Ezelith

class Valentines_Ezelith(Adv):
    conf = {}
    conf['slots.a'] = ['Forest_Bonds', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s
        `s3, not buff(s3) and fsc
        `s2
        `s1
        `s4
        `fs, seq=4
    """
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Summer_Patia']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
