from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Xainfried

class Xainfried(Adv):
    a1 = ('dc', 4)
    a3 = ('dt', 0.25)
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+His_Clever_Brother() # no more poison lol
    conf['slots.d'] = Gaibhne_and_Creidhne()
    conf['acl'] = """
        `dragon.act('c3 s end')
        `s3
        `s2
        `s4
        `s1, fsc
        `fs, x=5
        """
    coab = ['Summer_Celliera', 'Yurius', 'Renee']
    share = ['Gala_Elisanne', 'Eugene']
    conf['afflict_res.frostbite'] = 0

    def s1_proc(self, e):
        with KillerModifier('s1_killer', 'hit', 0.30, ['frostbite']):
            self.dmg_make(e.name, 2.30)
            self.add_hits(1)
            self.afflics.frostbite(e.name,120,0.41)
            self.dmg_make(e.name, 6.90)
            self.add_hits(3)

    def s2_proc(self, e):
        self.dragonform.charge_gauge(100)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
