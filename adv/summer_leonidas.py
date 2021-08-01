from core.advbase import *


class Summer_Leonidas(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[Selfbuff("dragondrive", 0.5, -1, "a", "passive")],
                fs=True,
                s1=True,
            )
        )


variants = {None: Summer_Leonidas}
