from core.advbase import *
from slot.a import *

def module():
    return Rawn

class Rawn(Adv):
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+The_Red_Impulse()
    conf['acl'] = """
        `dragon, fsc or s
        `s3
        `s2
        `s1
        `s4, cancel
        `fs, x=5
        """
    coab = ['Cleo','Raemond','Peony']
    share = ['Gala_Mym']

    def s1_proc(self, e):
        Debuff(e.name, 0.05, 10, 0.4, 'attack').on()

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)