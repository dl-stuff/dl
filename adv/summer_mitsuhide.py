from core.advbase import *


class Summer_Mitsuhide(Adv):

    def prerun(self):
        self.a1_spd_mod = Modifier("a1_spd", "spd", "passive", 0.10, get=self.a1_get)
        self.sunflowers = 0

    def a1_get(self):
        return self.s1.sp == self.s1.charged

    def s1_proc(self, e):
        if e.group == "sunflower":
            self.sunflowers -= 1
            if self.sunflowers == 0:
                self.current_s["s1"] = "default"

    def s2_proc(self, e):
        if self.sunflowers < 3:
            self.sunflowers += 1
        self.current_s["s1"] = "sunflower"


variants = {None: Summer_Mitsuhide}
