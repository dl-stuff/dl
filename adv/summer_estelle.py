from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Summer_Estelle

class Summer_Estelle(Adv):
    conf = {}
    conf['slots.a'] = Candy_Couriers()+Proper_Maintenance()
    conf['slots.frostbite.a'] = conf['slots.a']
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-end), s
        `s2
        `s3
        `s4, x>2
        `s1, x=5
        """
    conf['coabs'] = ['Hunter_Sarisse', 'Renee', 'Tobias']
    conf['share'] = ['Patia', 'Summer_Luca']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
