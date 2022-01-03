from conf import DEFAULT
from core.advbase import *


class Shingen(Adv):
    comment = "always use as many taps as possible for s1"

    def prerun(self):
        self.shingen_heal_burst = BurstGambit("heal_burst", 30, self.heal_burst_on, self.heal_burst_off)
        self.furinkazan_mode = ModeManager(
            "furinkazan_mode",
            group="furinkazan",
            buffs=[Selfbuff("furinkazen_att", 0.2, 30, "att", "passive"), Selfbuff("furinkazen_actdown", 0.5, 30, "ex", "actdown")],
            duration=30,
            x=True,
            s1=True,
            s2=True,
            source="s1",
            pause=("s",),
        )
        self.fervor = 0

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.rebind_function(Shingen, "heal_burst_on")
        adv.rebind_function(Shingen, "heal_burst_off")
        adv.shingen_heal_burst = BurstGambit("heal_burst", 30, adv.heal_burst_on, adv.heal_burst_off)
        adv.fervor = 0

    def heal_burst_on(self):
        self.heal_value = self.heal_formula("heal_burst", 140)

    def heal_burst_off(self):
        self.heal_make("heal_burst", self.heal_value, target="team", fixed=True)
        self.heal_value = 0

    def s1_before(self, e):
        self.shingen_heal_burst.on()

    def s1_proc(self, e):
        if e.group == DEFAULT and self.fervor == 3:
            self.fervor = 0
            self.furinkazan_mode.on()

    def s2_proc(self, e):
        self.fervor = min(3, self.fervor + 1)


variants = {None: Shingen}
