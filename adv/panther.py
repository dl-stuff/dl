from core.advbase import *


class Panther(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(group="ddrive", x=True, s1=True, s2=True), drain=75)
        self.a3_buffcount = 0
        self.a3_mod = Modifier("a3_flame_att", "flame", "ele", 0.0)
        Event("scorchrend").listener(self.a3_res_buff_proc)
        self.s2_res_down = Debuff("s2_res_down", 0.05, 30, 1, "flame_resist", "down", source="s2")

    def x_ddrive_proc(self, e):
        if e.base in ("x3", "x5"):
            self.dmg_make("x_carmen", 6.0)

    def a3_res_buff_proc(self, e):
        if self.nihilism:
            return
        if self.a3_buffcount < 3 and e.rate:
            self.a3_buffcount = min(3, self.a3_buffcount + e.rate)
            self.a3_mod.mod_value = self.a3_buffcount * 0.10


class Panther_DISPEL(Panther):
    comment = "s2 always dispel"

    def s2_proc(self, e):
        self.s2_res_down.on()


variants = {None: Panther, "DISPEL": Panther_DISPEL}
