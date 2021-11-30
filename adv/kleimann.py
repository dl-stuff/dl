from core.advbase import *


class Kleimann(Adv):
    # madness interactions tested ingame 11/18/2021
    def a1_madness_autocharge(self, t):
        self.add_hp(-self.madness_status)
        if self.nihilism:
            return
        self.charge("madness_autocharge", self.madness_status * 100)

    @property
    def madness(self):
        return self.fs_alt.uses

    def prerun(self):
        self.madness_status = 0
        self.fs_alt_uses = 5
        self.madness_timer = Timer(self.a1_madness_autocharge, 2.9, 1)
        self.fs_alt = FSAltBuff("a1_madness", "kleimann", uses=1)

    def fs_kleimann_proc(self, e):
        if self.madness_status < 5:
            self.madness_status += 1
            if self.madness_status == 1:
                self.madness_timer.on()
        if not self.nihilism:
            Selfbuff("madness", duration=-1, mtype="dummy").on()

    def s2_proc(self, e):
        if not self.fs_alt.get() and self.fs_alt_uses:
            self.fs_alt.on()
            self.fs_alt_uses -= 1


class Kleimann_MAX_MADNESS(Kleimann):
    SAVE_VARIANT = False
    comment = "max madness level"

    def prerun(self):
        super().prerun()
        self.madness_status = 5
        self.fs_alt_uses = 5
        self.madness_timer.on()
        if not self.nihilism:
            for _ in range(5):
                Selfbuff("madness", duration=-1, mtype="dummy").on()


variants = {None: Kleimann, "MADNESS": Kleimann_MAX_MADNESS}
