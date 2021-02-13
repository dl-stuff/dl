from core.advbase import *

# s2 only, unlike galex
class Skill_Reservoir(Skill):
    def charge(self, sp):
        self.charged = min(self.sp * 3, self.charged + sp)
        if self.charged >= self.sp * 3:
            self.skill_charged()

    def check(self):
        return self.flames and super().check()

    @property
    def count(self):
        return self.charged // self.sp


class Chrom(Adv):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.a_s_dict["s2"] = Skill_Reservoir("s2")
        self.a_s_dict["s2"].flames = 0

    def s1_proc(self, e):
        if self.s2.flames < 3:
            self.s2.flames += 1

    def s2_proc(self, e):
        with KillerModifier("s2_killer", "hit", 0.2, AFFLICT_LIST):
            hit1, hit2 = 2.93, 3.58
            if self.s2.flames == 3 and self.s2.count == 2:
                hit1, hit2 = 25.55, 26.31
                self.s2.charged = 0
            elif self.s2.flames == 2:
                hit1, hit2 = 7.20, 8.01
            self.dmg_make(e.name, hit1)
            self.add_combo()
            self.dmg_make(e.name, hit2)
            self.add_combo()
        self.s2.flames = 0


variants = {None: Chrom}
