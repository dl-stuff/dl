from core.advbase import *


class Kleimann(Adv):
    # madness interactions tested ingame 04/25/2021
    def a1_madness_autocharge(self, t):
        self.set_hp(self.hp - self.madness_degen)
        if self.nihilism:
            return
        for s in self.skills:
            if s.charged < s.sp:
                sp = self.madness_status * 100
                s.charge(sp)
                log("sp", s.name + "_autocharge", int(sp))

    @property
    def madness(self):
        return self.fs_alt.uses

    def prerun(self):
        self.madness_status = 0
        self.madness_degen = 0
        self.fs_alt_uses = 0
        self.madness_timer = Timer(self.a1_madness_autocharge, 2.9, 1)
        self.fs_alt = FSAltBuff("a1_madness", "madness", uses=1)
        Event("dragon").listener(self.reset_madness_degen)

    def fs_madness_proc(self, e):
        if self.madness_status < 5:
            self.madness_status += 1
            self.madness_degen += 1
            if self.madness_status == 1:
                self.madness_timer.on()

    def reset_madness_degen(self, e):
        self.madness_degen = 0

    def s2_proc(self, e):
        if not self.fs_alt.get() and self.fs_alt_uses < 5:
            self.fs_alt.on()
            self.fs_alt_uses += 1


class Kleimann_MAX_MADNESS(Kleimann):
    SAVE_VARIANT = False
    comment = "max madness level"

    def prerun(self):
        super().prerun()
        self.madness_status = 5
        self.madness_degen = 5
        self.madness_timer.on()


variants = {None: Kleimann, "MADNESS": Kleimann_MAX_MADNESS}
