from core.advbase import *
from slot.a import *

def module():
    return Valentines_Orion

class Valentines_Orion(Adv):
    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon,s
        `s3, fsc and not buff(s3)
        `s4,fsc
        `s1,cancel
        `fs, x=2
    """
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['afflict_res.burn'] = 0
    conf['share'] = ['Kleimann']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
