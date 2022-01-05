from conf import DEFAULT
from core.advbase import *


class Shingen(Adv):
    comment = "always use as many taps as possible for s1; fs always counters"

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
        self.mettle = 0

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.current_s[dst] = "furinkazan"
        adv.rebind_function(Shingen, "heal_burst_on")
        adv.rebind_function(Shingen, "heal_burst_off")
        adv.shingen_heal_burst = BurstGambit("heal_burst", 30, adv.heal_burst_on, adv.heal_burst_off)
        adv.mettle = 0

    @allow_acl
    def s(self, n):
        if not self.furinkazan_mode.get():
            if self.mettle == 0:
                self.current_s["s1"] = DEFAULT
            else:
                self.current_s["s1"] = f"mettle{self.mettle}"
        return super().s(n)

    def heal_burst_on(self):
        self.heal_value = self.heal_formula("heal_burst", 140)

    def heal_burst_off(self):
        self.heal_make("heal_burst", self.heal_value, target="team", fixed=True)
        self.heal_value = 0

    def s1_before(self, e):
        self.shingen_heal_burst.on()

    def s1_mettle3_hit3(self, *args):
        self.furinkazan_mode.on()


variants = {None: Shingen}
