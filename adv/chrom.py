from core.advbase import *
from slot.a import *
from slot.d import *
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
    a1 = ('a', 0.15, 'hp100')

    conf = {}
    conf['slots.a'] = The_Shining_Overlord()+The_Fires_of_Hate()
    conf['acl'] = """
        `dragon, s
        `s3, fsc and not self.s3_buff
        if self.sim_afflict
        `s4, fsc and (self.energy() = 0 or self.s2.count=3)
        `s2, self.s2.flames=3 and self.s2.count=3 and self.afflics.burn.get() and (self.energy()=0 or self.s4.charged < self.s4.sp - 1000)
        else
        `s4, fsc
        `s2, self.s2.flames=3 and self.s2.count=3 and (self.afflics.burn.get() or self.afflics.poison.get())
        end
        `s1, fsc
        `fs, x=2 and self.s1.charged >=1682
        `fs, x=3
    """
    coab = ['Blade', 'Wand', 'Marth']
    share = ['Kleimann']

    def d_skillshare(self):
        if self.sim_afflict:
            share = ['Nadine']

    def init(self):
        del self.slots.c.coabs['Sword']

    def prerun(self):
        self.s2 = Skill_Reservoir('s2', self.conf.s2)
        self.s2.flames = 0
        self.s2_woke = False

    def s1_proc(self, e):
        if self.s2.flames < 3:
            self.s2.flames += 1

    def s2_proc(self, e):
        with KillerModifier('s2_killer', 'hit', 0.2, AFFLICT_LIST):
            if self.s2.flames == 3 and self.s2.count == 2:
                self.dmg_make(e.name, 51.86)
                self.s2.charged = 0
            else:
                if self.s2.flames == 1:
                    self.dmg_make(e.name, 6.51)
                else:
                    self.dmg_make(e.name, 15.21)
        self.s2.flames = 0

if __name__ == '__main__':
    from core.simulate import test_with_argv
    test_with_argv(None, *sys.argv)