from core.advbase import *

class Hanabusa(Adv):
    def prerun(self):
        self.s1_stance = EffectBuff('dance_of_blades', 0, lambda: None, self.s1_stance_end)

    def s1_proc(self, e):
        if e.group == 0:
            self.s1_stance.on(20)
        elif e.group == 1:
            self.s1_stance.on(15)
        elif e.group == 2:
            self.s1_stance_end()

    def s2_before(self, e):
        self.s2_bt_mod = Modifier('s2_bt', 'buff', 'time', 0.20*self.current_s['s1']).on()

    def s2_proc(self, e):
        self.s2_bt_mod.off()

    def s1_stance_end(self):
        self.current_s['s1'] = 0

variants = {None: Hanabusa}
