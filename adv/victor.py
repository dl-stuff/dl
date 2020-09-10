from core.advbase import *
from module.bleed import Bleed, mBleed
from slot.a import *

def module():
    return Victor

class Victor(Adv):
    a1 = ('a',0.13,'hp70')
    a3 = ('bt',0.30)
    conf = {}
    conf['slots.a'] = Resounding_Rendition()+Primal_Crisis()
    conf['acl'] = """
        `dragon(c3-s-end), s4.check()
        `s3, not buff(s3)
        `s4, x=5
        `s1, self.bleed._static['stacks'] < 3
        `s2, x=5
        """
    conf['coabs'] = ['Akasha','Dragonyule_Xainfried','Lin_You']
    conf['share'] = ['Curran']

    def prerun(self):
        random.seed()
        self.bleed_class = Bleed
        self.bleed = self.bleed_class('g_bleed',0).reset()
        self.bleed_rate = 0.8

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.bleed_class = mBleed
        adv.bleed = adv.bleed_class('g_bleed',0).reset()
        adv.bleed_rate = 1

    def s1_proc(self, e):
        if random.random() < self.bleed_rate:
            self.bleed_class(e.name, 1.46).on()


if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
