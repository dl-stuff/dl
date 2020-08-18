from core.advbase import *
from slot.a import *
from slot.d import *

def module():
    return Yukata_Curran

default_rebound = 1

class Yukata_Curran(Adv):
    a3 = ('epassive_att_crit', 3)

    conf = {}
    conf['slots.a'] = Twinfold_Bonds()+Memories_of_Summers_Dusk()
    conf['slots.paralysis.a'] = conf['slots.a']
    conf['acl'] = """
        `dragon
        `s1
        `s2
        `s3
        `s4
        `fs, x=5
        """
    coab = ['Blade','Wand','Peony']
    share = ['Ranzal']
    conf['afflict_res.stun'] = 80
    conf['afflict_res.paralysis'] = 0

    def prerun(self):
        self.maskable_faith = False
        self.s1_rebound = default_rebound
        self.s1_ehits = 0
        self.s1_bullet = { False: 3, True: 5 }
        self.s2_hits = 30

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.maskable_faith = False
        adv.s1_rebound = default_rebound
        adv.s1_ehits = -float('inf')
        adv.s1_bullet = { False: 3, True: 5 }

    def s1_proc(self, e):
        bullet = self.s1_bullet[self.maskable_faith]
        old_hits = self.hits
        self.dmg_make(e.name, bullet*1.10)
        self.s1_ehits += self.add_hits(bullet)
        if self.maskable_faith:
            self.afflics.paralysis(e.name, 120, 0.97)
        for p in range(1, self.s1_rebound):
            self.dmg_make(f'{e.name}_rebound_{p}', bullet*1.10, attenuation=(0.55, p))
            self.add_hits(bullet)
        if self.s1_ehits > 10:
            self.s1_ehits -= 10
            # can gain energy during skill
            self.energy.add(5, queue=True)

    def s2_proc(self, e):
        if self.maskable_faith:
            self.afflics.stun(e.name, 100)
            self.dmg_make(e.name, 0.9*self.s2_hits)
        elif self.condition('hp50'):
            self.maskable_faith = True

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)