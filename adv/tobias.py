from core.advbase import *

class TobiasXAlt(XAltBuff):
    def enable_x(self, enabled):
        super().enable_x(enabled)
        try:
            self.adv.a_fs_dict['default'].set_enabled(not enabled)
            self.adv.a_dodge.enabled = not enabled
        except (KeyError, AttributeError):
            pass

class Tobias(Adv):
    def prerun(self):
        self.s1.autocharge_init(85)
        self.s2.charge(1) # 1 sp/s regen
        self.s2_x_alt = TobiasXAlt(group='sacred')
        self.s2_sp_buff = EffectBuff('sacred_blade', 10, lambda: self.s1.autocharge_timer.on(), lambda: self.s1.autocharge_timer.off())

    def s2_proc(self, e):
        if e.group == 'enhanced':
            self.s2_x_alt.on(10)
            self.s2_sp_buff.on(7)
        else:
            self.s2_x_alt.off()
            self.s2_sp_buff.off()
        self.s2.charge(1) # 1 sp/s regen

variants = {None: Tobias}
