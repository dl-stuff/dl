from core.advbase import *


class Peony(Adv):
    comment = "team skill prep not considered"

    def fs_peonydreams_proc(self, e):
        self.a1_cd_timer.on(20)

    def a1_cd(self, t):
        log("a1_cd", "end")
        self.a1_is_cd = False
        if self.a1_charge_defer:
            self.fs_alt.on()
            self.a1_charge_defer = False

    def prerun(self):
        self.fs_alt = FSAltBuff(group="peonydreams", uses=1)
        self.a1_is_cd = False
        self.a1_charge_defer = False
        self.a1_cd_timer = Timer(self.a1_cd)

    @staticmethod
    def prerun_skillshare(self, dst_key):
        self.a1_is_cd = False
        self.fs_alt = Dummy()

    def s2_proc(self, e):
        if self.a1_is_cd:
            self.a1_charge_defer = True
        else:
            self.fs_alt.on()


variants = {None: Peony}
