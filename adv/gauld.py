from core.advbase import *
from slot.d import *
from slot.a import *

def module():
    return Gauld

class Gauld(Adv):
    comment = 's2 after s1'
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+His_Clever_Brother()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-c3-end), s and (not s2.check() or not s=2)
        `s1, s=2
        `s4
        `s3
        `s1, cancel
        `s2, s=1
        `fs, x=5
        """
    conf['coabs'] = ['Blade', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']
    conf['afflict_res.frostbite'] = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)