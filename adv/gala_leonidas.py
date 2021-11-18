from core.advbase import *


class Gala_Leonidas(Adv):
    def prerun(self):
        self.draconian_grace = MultiLevelBuff(
            "draconian_grace",
            [
                Selfbuff(f"draconian_grace_lv{lv}", buffattrs[0], buffattrs[1], "att", "buff", source="s2")
                for lv, buffattrs in enumerate(((0.0, 40), (0.05, 40), (0.05, 40), (0.1, 40), (0.1, -1)), start=1)
            ],
        )
        self.draconian_grace_dtime = Modifier("draconian_grace_dtime", "dt", "leonidas", -0.5).off()
        self.draconian_grace_endshift = Listener("dragon_end", self.reset_draconian_grace).off()

    def upgrade_draconian_grace(self):
        self.draconian_grace.on()
        if self.draconian_grace.level == 5:
            self.dragonform.shift_cost //= 2
            self.draconian_grace_dtime.on()
            self.draconian_grace_endshift.on()

    def reset_draconian_grace(self, t=None):
        if self.draconian_grace.level == 5:
            self.dragonform.shift_cost *= 2
            self.draconian_grace_dtime.off()
        self.draconian_grace.off()
        self.draconian_grace_endshift.off()

    def s2_hit1(self, *args):
        self.upgrade_draconian_grace()


variants = {None: Gala_Leonidas}
