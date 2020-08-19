from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Cibella

class Cibella(Adv):
    conf = {}
    conf['slots.frostbite.a'] = Resounding_Rendition()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end'),s
        `s4
        `s3, cancel
        `s2, cancel
        `fs, seq=5
        """
    coab = ['Blade', 'Xander', 'Summer_Estelle']
    share = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
