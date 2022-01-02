from core.advbase import *


class Izumo(Adv):
    def prerun(self):
        self.heal_burst = BurstGambit("heal_burst", 5, self.heal_burst_on, self.heal_burst_off)
        self.resist_burst = BurstGambit("resist_burst", 3, self.resist_burst_on, self.resist_burst_off)
        self.resist_burst_buff = Teambuff("resist_burst", 0.1, 45, "res", "water")

    def heal_burst_on(self):
        self.heal_value = self.heal_formula("heal_burst", 45)

    def heal_burst_off(self):
        self.heal_make("heal_burst", self.heal_value, target="team", fixed=True)
        self.heal_value = 0

    def resist_burst_on(self):
        pass

    def resist_burst_off(self):
        self.resist_burst_buff.on()

    def s1_before(self, e):
        self.heal_burst.on()

    def s2_before(self, e):
        self.resist_burst.on()


variants = {None: Izumo}
