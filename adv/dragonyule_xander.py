from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Dragonyule_Xander

class Dragonyule_Xander(Adv):
    conf = {}
    conf['slots.a'] = CC()+PC()
    conf['slots.frostbite.a'] = CC()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end)
        `s3
        `s4
        `s1, cancel
    """
    conf['coabs'] = ['Renee', 'Blade', 'Bow']
    conf['share'] = ['Gala_Elisanne', 'Eugene']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)