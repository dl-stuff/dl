from core.advbase import *


class Vania(Adv):
    def prerun(self):
        self.blood_pact = 0

    def s1_proc(self, t):
        if self.blood_pact < 5:
            self.blood_pact += 1
        if self.blood_pact == 5 and self.current_s["s1"] != "bloodpact":
            self.current_s["s1"] = "bloodpact"
            self.s2.autocharge_init(497).on()


variants = {None: Vania}
