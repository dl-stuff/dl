from core.advbase import *


class Radiant_Xuan_Zang(Adv):
    def prerun(self):
        self.fs_alt = FSAltBuff(group="xihe", uses=1)
        self.xihe_gauge = 0
        self.xihe_gauge_gain = 50

    def s1_proc(self, e):
        if e.group == "xihe":
            self.current_s["s1"] = "default"

    def s2_proc(self, e):
        if e.group == "xihe":
            self.current_s["s2"] = "default"
        else:
            self.xihe_gauge += self.xihe_gauge_gain
            log("debug", "xihe", self.xihe_gauge)
            if self.xihe_gauge >= 100:
                self.xihe_gauge = 0
                self.fs_alt.on()
                self.current_s["s1"] = "xihe"
                self.current_s["s2"] = "xihe"


variants = {None: Radiant_Xuan_Zang}
