from conf import DEFAULT
from core.advbase import *


class Humanoid_Zodiark(Adv):
    def prerun(self):
        Event("dragon").listener(self.a1_on, order=0)
        self.spite_debuff = MultiLevelBuff(
            "spite",
            [
                Selfbuff("spite_lv1", 0.15, 10, "killer", "passive", source="x3"),
                Selfbuff("spite_lv2", 0.15, 10, "killer", "passive", source="x3"),
                Selfbuff("spite_lv3", 0.15, 10, "killer", "passive", source="x3"),
                Selfbuff("spite_lv4", 0.15, 15, "killer", "passive", source="x3"),
                Selfbuff("spite_lv5", 0.15, 20, "killer", "passive", source="x3"),
            ],
        )
        self.malevolent_rush = 0

    @property
    def spite(self):
        return self.spite_debuff.level

    def a1_on(self, e):
        if self.dshift_count == 2:
            for act in self.dragonform.conf.values():
                try:
                    if act["attr"] and act["attr_HAS"]:
                        act["attr"] = act["attr_HAS"]
                except TypeError:
                    pass

    def s1_proc(self, e):
        self.current_x = "mode2"
        self.malevolent_rush = 3

    def x_mode2_proc(self, e):
        if e.index == 3:
            self.spite_debuff.on()
            self.malevolent_rush -= 1
            if self.malevolent_rush == 0:
                self.current_x = DEFAULT


variants = {None: Humanoid_Zodiark}
