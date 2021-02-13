from core.advbase import *


class Gala_Chelle(Adv):
    def prerun(self):
        self.royal_pride_buffs = []
        self.royal_pride_zone = ZoneTeambuff("royal_pride", 1, -1, "royal", "pride")
        self.a3_modifier = Modifier("a3_fs_per_buff", "fs", "passive", 0.0)
        self.a3_modifier.get = self.a3_mod_value

    def a3_mod_value(self):
        return min(0.3, self.buffcount * 0.02)

    def s2_proc(self, e):
        if self.royal_pride < 10:
            self.royal_pride_buffs.append(
                Selfbuff("a1_royal_pride", 1, -1, "royal", "pride").on()
            )
        if not self.royal_pride_zone.get() and self.royal_pride >= 5:
            self.royal_pride_zone.on()

    @property
    def royal_pride(self):
        return len(self.royal_pride_buffs)


variants = {None: Gala_Chelle}
