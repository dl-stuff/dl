from core.advbase import *


class Kleimann(Adv):
    def d_coabs(self):
        if self.duration <= 60:
            self.conf["coabs"] = ["Ieyasu", "Gala_Alex", "Bow"]

    def a1_madness_autocharge(self, t):
        if self.nihilism:
            return
        for s in self.skills:
            if s.charged < s.sp:
                sp = self.madness_status * 100
                s.charge(sp)
                log("sp", s.name + "_autocharge", int(sp))
        self.set_hp(self.hp - 1)

    @property
    def madness(self):
        return self.fs_alt.uses

    def prerun(self):
        self.madness_status = 0
        self.madness_timer = Timer(self.a1_madness_autocharge, 2.9, 1)
        self.fs_alt = FSAltBuff("a1_madness", "madness", uses=0)

    def fs_madness_proc(self, e):
        if self.madness_status < 5:
            self.madness_status += 1
            if self.madness_status == 1:
                self.madness_timer.on()

    def s2_proc(self, e):
        if not self.fs_alt.get():
            self.fs_alt.on()
        if self.fs_alt.uses < 5:
            self.fs_alt.uses += 1


variants = {None: Kleimann}
