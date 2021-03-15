from core.advbase import *
from module.template import ArmamentAdv


class Finni(ArmamentAdv):
    def __init__(self, **kwargs):
        super().__init__(true_sp=999999, maxcharge=2, **kwargs)

    def more_than_one_gauge(self):
        return self.sr.count >= 1

    def prerun(self):
        self.config_armament(autocharge=80000)
        self.a3_modifiers = (
            Modifier("a3_att", "att", "passive", 0.2, get=self.more_than_one_gauge),
            Modifier("a3_spd", "spd", "passive", 0.15, get=self.more_than_one_gauge),
        )
        self.s2_combo = 0
        self.s2_autocharge_buff = EffectBuff("s2_autocharge_buff", 30, self.autocharge_buff_on, self.autocharge_buff_off, source="s2")

    def autocharge_buff_on(self):
        self.sr.autocharge_sp = 160000

    def autocharge_buff_off(self):
        self.sr.autocharge_sp = 80000

    def add_combo(self, name="#"):
        result = super().add_combo(name=name)
        if name.startswith("s2"):
            self.s2_combo += self.echo
        return result

    def s2_before(self, e):
        self.s2_combo = 0

    def s2_proc(self, e):
        if self.s2_combo >= 6:
            self.s2_autocharge_buff.on()


variants = {None: Finni}
