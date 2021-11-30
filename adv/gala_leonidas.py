from core.advbase import *


class Gala_Leonidas(Adv):
    def prerun(self):
        self.draconian_grace = MultiLevelBuff(
            "draconian_grace",
            [
                Selfbuff(f"draconian_grace_lv{lv}", val, 40, "att", "buff", source="s2")
                for lv, val in enumerate((0.0, 0.05, 0.05, 0.1), start=1)
            ].append(
                MultiBuffManager(
                    "draconian_grace_lv5",
                    [
                        Selfbuff("draconian_grace_lv5_att", 0.1, -1, "att", "buff", source="s2"),
                        EffectBuff("draconian_grace_dshift", -1, self.draconian_grace_dshift_on, self.draconian_grace_dshift_off, source="s2"),
                    ]
                )
            )
        )
        self.draconian_grace_dtime = Modifier("draconian_grace_dtime", "dt", "leonidas", -0.5).off()
        self.draconian_grace_endshift = Listener("dragon_end", lambda _: self.draconian_grace.off()).off()

    def draconian_grace_dshift_on(self):
        self.dragonform.shift_cost //= 2
        self.draconian_grace_dtime.on()
        self.draconian_grace_endshift.on()

    def draconian_grace_dshift_off(self):
        self.dragonform.shift_cost *= 2
        self.draconian_grace_dtime.off()
        self.draconian_grace_endshift.off()

    def s2_hit1(self, *args):
        self.draconian_grace.on()


variants = {None: Gala_Leonidas}
