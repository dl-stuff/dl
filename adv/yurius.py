from core.advbase import *

class Yurius(Adv):
    def prerun(self):
        self.dragondrive = self.dragonform.set_dragondrive(ModeManager(
            group='ddrive',
            buffs=[
                Selfbuff('dragondrive_sd', 0.35, -1, 's', 'passive'),
                Selfbuff('dragondrive_sp',0.30, -1, 'sp', 'buff')
            ],
            s1=True, s2=True
        ), drain=75)

variants = {None: Yurius}
