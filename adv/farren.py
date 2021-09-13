from core.advbase import *


class Farren(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[Selfbuff("dragondrive", 0.2, -1, "defense", "passive")],
                x=True,
                fs=True,
                s1=True,
                s2=True,
            ),
            drain=50,
        )
        self.a3_regen = Timer(self.a3_regen, 1.0, True).on()

    def s2_proc(self, e):
        if e.group == "default":
            self.add_hp(140 * self.dragonform.dragon_gauge / 3000)
            self.dragonform.charge_gauge(-self.dragonform.dragon_gauge, utp=True, dhaste=False)

    def a3_regen(self, t):
        if self.amp_lvl(kind="team", key=3) >= 1:
            self.dragonform.charge_gauge(1.5, utp=True, dhaste=False, percent=True)


variants = {None: Farren}
