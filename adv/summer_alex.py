from core.advbase import *


class Summer_Alex(Adv):
    conf = {
        "acl": """
            `dragon(c2-s-c2-c2-c2-c2-end), cancel
            `s3, not buff(s3)
            `s2
            `s1, s2.charged < 4000 or s=2
            `s4, cancel
            `fs, x=5
        """
    }

    def prerun(self):
        self.scorchbloom = 0
        self.sb_t = Timer(self.scorchbloom_proc)

    def s2_proc(self, e):
        if self.berserk_mode:
            self.scorchbloom = 0
        else:
            self.scorchbloom = self.dmg_formula("s", 14.32)
            self.scorchbloom_rend = self.dmg_formula("afflic", 0.416)
            self.scorchbloom_rate = self.afflics.scorchrend.rate
            self.scorchbloom_time = self.afflics.scorchrend.time
        self.sb_t.name = e.name
        self.sb_t.on(30)

    def scorchbloom_proc(self, t=None):
        if self.scorchbloom > 0:
            self.dmg_make(f"s2_scorchbloom", self.scorchbloom, fixed=True)
            self.afflics.scorchrend.on("s2", self.scorchbloom_rate, 0, dmg_override=self.scorchbloom_rend, time_override=self.scorchbloom_time)
            self.scorchbloom = 0
            self.scorchbloom_rend = 0
            self.scorchbloom_rate = 0
            self.scorchbloom_time = 0
            self.sb_t.off()
            return True
        return False

    def s1_enhanced_hit2(self, name, base, group, aseq):
        self.scorchbloom_proc()


variants = {None: Summer_Alex}
