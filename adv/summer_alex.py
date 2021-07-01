from core.advbase import *


class Summer_Alex(Adv):

    def prerun(self):
        self.scorchbloom = 0
        self.sb_t = Timer(self.scorchbloom_proc)

    def s2_proc(self, e):
        if self.berserk_mode:
            self.scorchbloom = 0
        else:
            self.scorchbloom = self.dmg_formula("s", 14.32)
            self.scorchbloom_rend = self.dmg_formula("afflic", 0.416)
        self.sb_t.name = e.name
        self.sb_t.on(30)

    def scorchbloom_proc(self, t):
        if self.scorchbloom > 0:
            self.dmg_make(f"{t.name}_scorchbloom", self.scorchbloom, fixed=True)
            self.afflics.scorchrend.on(t.name, 120, 0)
            scorch_dot = Dot(f"{t.name}_scorchbloom_scorchrend", 0, 21, 2.9)
            scorch_dot.on()
            scorch_dot.tick_dmg = self.scorchbloom_rend
            self.scorchbloom = 0
            self.scorchbloom_rend = 0
            self.sb_t.off()
            return True
        return False

    def s1_hit2(self, name, base, group, aseq):
        if group == "enhanced":
            self.scorchbloom_proc(e)


variants = {None: Summer_Alex}
