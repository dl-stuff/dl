from core.advbase import *
from module.template import LowerMCAdv


class Gala_Elisanne(Adv):
    comment = "70MC"

    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()
        self.divine_revelation = Selfbuff("divine_revelation", 1, 13, "kb", "res", source="a1")
        self.ahits = 0
        Event("fs").listener(self.dr_proc)
        Event("s").listener(self.dr_proc)
        Event("ds").listener(self.dr_proc)

    def dr_proc(self, e):
        self.divine_revelation.on()

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        a_hits = self.hits // 10
        if a_hits > 0 and a_hits != self.ahits:
            self.ahits = a_hits
            self.divine_revelation.on()
        return result

    def s2_autocharge(self, t):
        if self.divine_revelation.get():
            log("sp", "s2_autocharge", 960)
            self.s2.charge(960)  # 2496 - 1536
        elif self.s2.charged < self.s2.sp:
            self.s2.charge(-1536)


class Gala_Elisanne_50MC(Gala_Elisanne, LowerMCAdv):
    pass


variants = {None: Gala_Elisanne, "50MC": Gala_Elisanne_50MC}
