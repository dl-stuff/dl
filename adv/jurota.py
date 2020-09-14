from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Jurota

class Jurota(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['slots.frostbite.a'] = Resounding_Rendition()+His_Clever_Brother()
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon(c3-s-c3-end), (self.afflics.frostbite.get() and s=3) or (not self.afflics.frostbite.get() and s=1)
        `s3
        `s4
        `s1, cancel
        """
    conf['coabs'] = ['Renee', 'Xander', 'Summer_Estelle']
    conf['share'] = ['Gala_Elisanne', 'Ranzal']

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)