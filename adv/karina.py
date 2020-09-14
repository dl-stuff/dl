from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Karina

class Karina(Adv):
    conf = {}
    conf['slots.a'] = Valiant_Crown()+Felyne_Hospitality()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end), s=1
        `s4
        `s3
        `s2
        `s1
    """
    conf['coabs'] = ['Tobias', 'Renee', 'Summer_Estelle']
    conf['share'] = ['Summer_Cleo', 'Patia']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)