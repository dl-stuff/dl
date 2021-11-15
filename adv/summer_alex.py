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
        self.sb_t.on(30)

    def scorchbloom_proc(self, t=None):
        if self.scorchbloom > 0:
            self.dmg_make("s2_scorchbloom", self.scorchbloom, fixed=True)
            self.afflics.scorchrend.on("s2_scorchbloom", 120, 0.416)
            self.scorchbloom = 0
            self.sb_t.off()
            return True
        return False

    def s1_enhanced_hit2(self, *args):
        self.scorchbloom_proc()


variants = {None: Summer_Alex}
