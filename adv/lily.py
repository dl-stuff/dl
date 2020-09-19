from core.advbase import *
from module.x_alt import X_alt
import wep.wand

def module():
    return Lily

class Lily(Adv):
    conf = {}
    conf['slots.a'] = ['Candy_Couriers', 'His_Clever_Brother']
    conf['slots.d'] = 'Gaibhne_and_Creidhne'
    conf['acl'] = """
        `dragon(c3-s-end), s
        `s3
        `s4
        `s2
        `s1
    """
    conf['coabs'] = ['Blade', 'Renee', 'Summer_Celliera']
    conf['share'] = ['Gala_Elisanne', 'Eugene']


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
