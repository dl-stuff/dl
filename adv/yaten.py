from conf import DEFAULT
from core.advbase import *
from module.template import LowerMCAdv


class Yaten(Adv):
    def prerun(self):
        Event("energy").listener(self.s1_upgrade)
        Event("energy_end").listener(self.s1_downgrade)
        self.s2_up_s1 = False

    def s1_upgrade(self, e):
        if e.stack >= 5:
            self.current_s["s1"] = "energized"

    def s1_downgrade(self, e):
        if not self.s2_up_s1:
            self.current_s["s1"] = DEFAULT

    def s1_proc(self, e):
        if e.group == "energized":
            self.s2_up_s1 = False
            self.s1_downgrade(e)

    def s2_proc(self, e):
        if self.MC is None:
            self.s2_up_s1 = True
            self.current_s["s1"] = "energized"


class Yaten_50MC(Yaten, LowerMCAdv):
    pass


variants = {None: Yaten, "50MC": Yaten_50MC}
