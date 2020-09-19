from core.advbase import *

def module():
    return Yukata_Curran

class Yukata_Curran(Adv):
    conf = {}
    conf['slots.a'] = ['Twinfold_Bonds', 'Spirit_of_the_Season']
    conf['acl'] = """
        `dragon
        `s3, not buff(s3)
        `s2
        `s4, x=5
        `s1, not self.energy()=5 and cancel
        `fs, x=5
        """
    conf['coabs'] = ['Sharena','Lucretia','Peony']
    conf['share'] = ['Summer_Patia']
    # conf['afflict_res.stun'] = 80
    conf['afflict_res.paralysis'] = 0
    conf['attenuation.hits'] = 2

    def prerun(self):
        self.s1_ehits = 0
        comment = f'assume {self.conf.attenuation} hits per s1 bullet'

    def add_combo(self, name='#'):
        super().add_combo(name)
        if name.startswith('s1'):
            self.s1_ehits += 1
        if self.s1_ehits >= 10:
            self.s1_ehits -= 10
            self.energy.add(5, queue=True)


    # def s1_proc(self, e):
        # bullet = self.s1_bullet[self.maskable_faith]
        # old_hits = self.hits
        # self.dmg_make(e.name, bullet*1.10)
        # self.s1_ehits += self.add_hits(bullet)
        # if self.maskable_faith:
        #     self.afflics.paralysis(e.name, 120, 0.97)
        # for p in range(1, self.s1_rebound):
        #     self.dmg_make(f'{e.name}_rebound_{p}', bullet*1.10, attenuation=(0.55, p))
        #     self.s1_ehits += self.add_hits(bullet)
        # if self.s1_ehits > 10:
        #     self.s1_ehits -= 10
        #     # can gain energy during skill
        #     self.energy.add(5, queue=True)

    # def s2_proc(self, e):
    #     if self.maskable_faith:
    #         self.afflics.stun(e.name, 100)
    #         self.dmg_make(e.name, 0.9*self.s2_hits)
    #     elif self.condition('hp50'):
    #         self.maskable_faith = True

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)