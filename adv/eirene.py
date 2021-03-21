from core.advbase import *
from module.template import ArmamentAdv


class Eirene(ArmamentAdv):
    def __init__(self, **kwargs):
        super().__init__(true_sp=999999, maxcharge=2, **kwargs)

    def prerun(self):
        self.config_armament(autocharge=100000)
        self.hp_event.listener(self.a3_heal)
        self.a3_cd = False

    def a3_cd_end(self, _):
        self.a3_cd = False

    def a3_heal(self, e):
        if e.hp <= 30 and (e.hp - e.delta) > 30 and not self.a3_cd:
            add_hp = self.sr.charged / (self.sr.sp * self.sr.maxcharge) * 70
            self.add_hp(add_hp)
            self.a3_cd = True
            Timer(self.a3_cd_end).on(90)
            self.sr.charged = 0


variants = {None: Eirene}
