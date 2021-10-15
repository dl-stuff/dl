from core.advbase import *
from module.template import Adv_INFUTP


class Panther(Adv):
    comment = "s2 ddrive always dispel"

    def prerun(self):
        self.a3_buffcount = 0
        self.a3_mod = Modifier("a3_flame_att", "flame", "ele", 0.0)
        Event("scorchrend").listener(self.a3_res_buff_proc)
        self.s2_res_down = Debuff("s2_res_down", 0.05, 30, 1, "flame_resist", "down", source="s2")

    def a3_res_buff_proc(self, e):
        if self.nihilism:
            return
        if self.a3_buffcount < 3 and e.rate:
            self.a3_buffcount = min(3, self.a3_buffcount + e.rate)
            self.a3_mod.mod_value = self.a3_buffcount * 0.10

    def s2_proc(self, e):
        if e.group == "ddrive":
            self.s2_res_down.on()


class Panther_INFUTP(Panther, Adv_INFUTP):
    comment = Panther.comment + ";" + Adv_INFUTP.comment


variants = {None: Panther, "INFUTP": Panther_INFUTP}
