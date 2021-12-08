from conf import DEFAULT
from core.advbase import *


class Gala_Gatov(Adv):
    comment = "s2 always counter"

    def prerun(self):
        self.charge_p("prep", 100, target="s2")
        self.buff2025 = 0
        self.dualsword_mode = ModeManager(group="dualsword", x=True, fs=True, s1=True, s2=True, duration=33.33, pause=("s", "dragon"))
        self.dualsword_mode.extra_effect_off(self.dualsword_end)

    @property
    def dualsword(self):
        return self.dualsword_mode.timeleft()

    def dualsword_end(self):
        self.s1.charged = 0
        self.s2.charged = 0

    def s1_before(self, e):
        if e.group == "dualsword":
            self.current_s["s2"] = "dualswordboosted"
        elif e.group == DEFAULT:
            self.dualsword_mode.on()
            self.charge_p("prep", 100, target=("s1", "s2"))

    def s1_proc(self, e):
        if e.group == "dualswordboosted":
            self.current_s["s1"] = "dualsword"
            self.buff2025 = 0

    def s2_before(self, e):
        if e.group == "dualsword":
            self.current_s["s1"] = "dualswordboosted"

    def s2_proc(self, e):
        if e.group == "dualswordboosted":
            self.current_s["s2"] = "dualsword"
            self.buff2025 = 0


variants = {None: Gala_Gatov}
