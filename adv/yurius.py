from core.advbase import *


class Yurius(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[
                    Selfbuff("dragondrive_sd", 0.35, -1, "s", "passive"),
                    Selfbuff("dragondrive_sp", 0.30, -1, "sp", "buff"),
                ],
                s1=True,
                s2=True,
            ),
            drain=75,
        )


class Yurius_DDRIVE(Yurius):
    SAVE_VARIANT = False
    comment = "infinite ddrive gauge"

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[
                    Selfbuff("dragondrive_sd", 0.35, -1, "s", "passive"),
                    Selfbuff("dragondrive_sp", 0.30, -1, "sp", "buff"),
                ],
                s1=True,
                s2=True,
            ),
            shift_cost=0,
            drain=0,
        )
        self.dragonform.charge_gauge(3000, utp=True, dhaste=False)


variants = {None: Yurius, "DDRIVE": Yurius_DDRIVE}
