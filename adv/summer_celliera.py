from core.advbase import *
from slot.a import *
from slot.d import *


def module():
    return Summer_Celliera

class Summer_Celliera(Adv):
    conf = {}
    conf['slots.a'] = Valiant_Crown() + Proper_Maintenance()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end)
        `s2
        `s3, fsc
        `s4, fsc
        `s1, fsc
        `fs, x=2
        """
    conf['coabs'] = ['Tobias', 'Hunter_Sarisse', 'Summer_Estelle']
    conf['afflict_res.bog'] = 100
    conf['share'] = ['Patia', 'Summer_Luca']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
