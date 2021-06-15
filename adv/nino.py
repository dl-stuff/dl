from core.advbase import *


class Nino(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[Selfbuff("dragondrive_att", 0.15, -1, "a", "passive"), Selfbuff("dragondrive_spd", 0.1, -1, "spd", "passive")],
                x=True,
                fs=True,
                s1=True,
                s2=True,
            )
        )


variants = {None: Nino}
