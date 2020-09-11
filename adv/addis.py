from core.advbase import *
from module.bleed import Bleed
from slot.a import *
from slot.d import *

def module():
    return Addis

class Addis(Adv):
    comment = 's2 c2 s1 c5fsf c4fs s1; hold s2s1 until bleed under 3'
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Breakfast_at_Valerios()
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s2, charged_in(s1, 2) and bleed.get() < 3
        `s1, not charged_in(s2, 3) and bleed.get() < 3
        `s4, xf=5 and not buff(s2)
        `fsf, xf=5
        """
    conf['coabs'] = ['Akasha','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']
    conf['afflict_res.poison'] = 0

    def getbleedpunisher(self):
        if self.bleed._static['stacks'] > 0:
            return 0.08
        return 0

    def prerun(self):
        random.seed()
        # self.s2buff = Selfbuff('s2_shapshifts1',1, 10,'ss','ss')
        # self.s2str = Selfbuff('s2_str',0.25,10)
        self.bleedpunisher = Modifier('bleed','att','killer',0.08)
        self.bleedpunisher.get = self.getbleedpunisher
        self.bleed = Bleed('g_bleed',0).reset()
        # self.crit_mod = self.rand_crit_mod

    def s1_enhanced_proc1(self, e):
        if random.random() < 0.8:
            Bleed(e.name, 1.32).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)