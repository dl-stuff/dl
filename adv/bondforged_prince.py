from core.advbase import *


class FsOnX(Fs):
    def __init__(self, name, conf, act=None):
        super().__init__(name, conf, act=act)
        self.retain_x = None

    def _cb_acting(self, e):
        super()._cb_acting(e)
        if isinstance(self.getprev(), X):
            self.retain_x = self.getprev()

    def _cb_act_end(self, e):
        super()._cb_act_end(e)


class Bondforged_Prince(Adv):
    DRAGONLIGHT_DT = 1 / 0.8 - 1

    def doconfig(self):
        super().doconfig()
        self.a_fs_dict["fs"] = FsOnX("fs", self.a_fs_dict["fs"].conf)
        self.a_dodge_on_x = self.a_fs_dict["fs"]
        Event("dragon").listener(lambda _: self.add_amp(amp_id="30000", max_level=3, target=2))

    def prerun(self):
        if self.condition("tempest charge"):
            self.dragonform.charge_dprep(50)
        Modifier("tempest_dt", "dt", "getrektoof", self.DRAGONLIGHT_DT).on()
        self.x4_jump = 0
        # Event("fs").listener(self.jump_fs)

    def fs_before(self, e):
        if self.action.getprev() == self.a_x_dict["default"][4]:
            self.x4_jump = 1
        else:
            self.x4_jump = 0


variants = {None: Bondforged_Prince}
