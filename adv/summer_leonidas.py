from core.advbase import *


class Summer_Leonidas(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[Selfbuff("dragondrive", 0.5, -1, "a", "passive")],
                fs=True,
                s1=True,
            ),
            drain=150
        )


class Summer_Leonidas_DDRIVE(Summer_Leonidas):
    SAVE_VARIANT = False
    comment = "infinite ddrive gauge"

    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[Selfbuff("dragondrive", 0.5, -1, "a", "passive")],
                fs=True,
                s1=True,
            ),
            drain=0
        )
        self.dragonform.charge_gauge(3000, utp=True, dhaste=False)


variants = {None: Summer_Leonidas, "INF_DDRIVE": Summer_Leonidas_DDRIVE}
