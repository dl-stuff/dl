from core.advbase import *


class Peony(Adv):
    comment = "team skill prep not considered"

    def fs_peonydreams_proc(self, e):
        self.set_cd("a1", 20, proc=self.a1_cd_end)

    def a1_cd_end(self, t):
        if self.a1_charge_defer:
            self.fs_alt.on()
            self.a1_charge_defer = False

    def prerun(self):
        self.fs_alt = FSAltBuff(group="peonydreams", uses=1)
        self.a1_charge_defer = False

    def s2_proc(self, e):
        if e.name != "s2":
            # shared skill, do not proc fs
            return
        if self._is_cd("a1"):
            self.a1_charge_defer = True
        else:
            self.fs_alt.on()


variants = {None: Peony}
