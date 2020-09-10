from core.advbase import *
from module.bleed import Bleed, mBleed
from slot.d import *
from slot.a import *

def module():
    return Sazanka

class Sazanka(Adv):
    a3 = ('k_sleep', 0.20)

    conf = {}
    conf['slots.a'] = Summer_Paladyns()+The_Fires_of_Hate()
    conf['slots.poison.a'] = Summer_Paladyns()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon(c3-s-end), s1.check()
        `s3, not self.s3_buff
        `s4
        `s1
    """
    conf['coabs'] = ['Ieyasu', 'Wand', 'Bow']
    conf['afflict_res.sleep'] = 80
    conf['share'] = ['Kleimann']

    def d_coabs(self):
        if self.sim_afflict:
            self.conf['share'] = ['Curran']

    def prerun(self):
        random.seed()
        self.bleed_class = Bleed
        self.bleed = self.bleed_class('g_bleed',0).reset()
        self.bleed_rate = 0.8

        # change to Fs_alt 1 day
        self.s2fscharge = 3

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.bleed_class = mBleed
        adv.bleed = adv.bleed_class('g_bleed',0).reset()
        adv.bleed_rate = 1

    def s1_proc(self, e):
        if random.random() < self.bleed_rate:
            self.bleed_class(e.name, 1.32).on()

    def s2_proc(self, e):
        self.s2fscharge = 3

    def fs_proc(self, e):
        if self.s2fscharge > 0:
            self.s2fscharge -= 1
            self.dmg_make(f'{e.name}_boost',0.38)
            self.afflics.sleep(f'{e.name}_fs', 100, 4.5)

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)
