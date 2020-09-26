from core.advbase import *
from core.afflic import AFFLICT_LIST

def module():
    return Chrom

# s2 only, unlike galex
class Skill_Reservoir(Skill):
    def charge(self, sp):
        self.charged = min(self.sp*3, self.charged + sp)
        if self.charged >= self.sp*3:
            self.skill_charged()

    def check(self):
        return self.flames and super().check()

    @property
    def count(self):
        return self.charged // self.sp

class Chrom(Adv):
    conf = {}
    conf['slots.a'] = [
    'The_Shining_Overlord',
    'Flash_of_Genius',
    'Me_and_My_Bestie',
    'Chariot_Drift',
    'Dueling_Dancers'
    ]
    conf['acl'] = """
        `dragon, s and not energy()=5
        `s3, fsc and not buff(s3)
        if self.sim_afflict
        `s4, fsc and (self.energy() = 0 or self.s2.count=3)
        `s2, self.s2.flames=3 and self.s2.count=3 and self.afflics.burn.get() and (self.energy()=0 or self.s4.charged < self.s4.sp - 1000)
        else
        `s4, fsc and not energy()=5
        `s2, self.s2.flames=3 and self.s2.count=3 and (self.afflics.burn.get() or self.afflics.poison.get())
        end
        `s1, fsc
        `fs, x=2 and self.s1.charged >=1682
        `fs, x=3
    """
    conf['coabs'] = ['Blade', 'Wand', 'Serena']
    conf['share.base'] = ['Kleimann']
    conf['share.burn'] = ['Nadine']

    def __init__(self, conf=None, cond=None):
        super().__init__(conf=conf, cond=cond)
        del self.slots.c.coabs['Sword']
        self.a_s_dict['s2'] = Skill_Reservoir('s2')
        self.a_s_dict['s2'].flames = 0

    def s1_proc(self, e):
        if self.s2.flames < 3:
            self.s2.flames += 1

    # 101501052: 1.4299999475479126 + 1.4900000095367432
    # 101501053: 2.930000066757202 + 3.5799999237060547
    # 101501054: 7.199999809265137 + 8.010000228881836
    # 101501055: 25.549999237060547 + 26.309999465942383
    def s2_proc(self, e):
        with KillerModifier('s2_killer', 'hit', 0.2, AFFLICT_LIST):
            hit1, hit2 = 2.93, 3.58
            if self.s2.flames == 3 and self.s2.count == 3:
                hit1, hit2 = 25.55, 26.31
                self.s2.charged = 0
            elif self.s2.flames == 2:
                hit1, hit2 = 7.20, 8.01
            self.dmg_make(e.name, hit1)
            self.add_combo()
            self.dmg_make(e.name, hit2)
            self.add_combo()
        self.s2.flames = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)