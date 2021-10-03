from core.advbase import *


class Summer_Mym(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(
            ModeManager(
                group="ddrive",
                buffs=[Selfbuff("dragondrive", 0.25, -1, "a", "passive")],
                x=True,
                fs=True,
                s1=True,
            )
        )


variants = {None: Summer_Mym}
