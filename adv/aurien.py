from core.advbase import *
from slot.a.all import *
from slot.d.flame import *

def module():
    return Aurien

class Aurien(Adv):
    comment = 'no s1'

    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Fires_of_Hate()
    conf['slots.burn.a'] = Resounding_Rendition()+Me_and_My_Bestie()
    conf['acl'] = """
        `dragon(c3-s-s-end), s
        `s4, fscf
        `s3, fscf
        `s2, cancel
        `dodge, fscf
        `fs, x=5
        """
    conf['afflict_res.burn'] = 0
    conf['coabs'] = ['Blade', 'Marth', 'Wand']
    conf['share'] = ['Summer_Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)