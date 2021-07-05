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
        self.enhanced_autos = 0
        self.enhanced_autos_buff = EffectBuff("enhanced_autos", 10, self.enhanced_autos_on, self.enhanced_autos_off, source="s1")

    def enhanced_autos_on(self):
        self.enhanced_autos = 1

    def enhanced_autos_off(self):
        self.enhanced_autos = 0

    def s1_before(self, e):
        if e.group == "ddrive":
            self.enhanced_autos_buff.on()


variants = {None: Summer_Mym}
