from core.advbase import *

def module():
    return Rena

class Rena(Adv):
    conf = {}
    conf['slots.a'] = ['Resounding_Rendition', 'Me_and_My_Bestie']
    conf['acl'] = """
        `dragon, s=1 and not s2.check()
        `s3, not buff(s3)
        `s1
        `s2, s=1
        `s4, x=5
        """
    conf['coabs'] = ['Wand', 'Serena', 'Marth']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
