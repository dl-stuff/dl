from core.advbase import *


class Summer_Norwin(Adv):
    def prerun(self):
        self.doleful = 0
        self.current_s["s1"] = "a"
        self.current_s["s2"] = "a"

    def s1_before(self, e):
        if e.group == "d":
            self.doleful = 0
            self.energy.unset_disabled("doleful")

    def s2_proc(self, e):
        if e.group == "d":
            self.set_hp(self.hp * (1 - self.doleful * 0.20))
            self.doleful = min(self.doleful + 1, 4)
            self.energy.set_disabled("doleful")


variants = {None: Summer_Norwin}
