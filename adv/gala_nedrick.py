from core.advbase import *


class Gala_Nedrick(Adv):
    soul_charge = 0

    def force_dp_amount(self, _):
        self.dragonform.max_dragon_gauge = 500
        self.dragonform.charge_dprep(100)
        self.dragonform.max_dragon_gauge = 1000
        self.dragonform.shift_cost = 1000

    def prerun(self):
        Timer(self.force_dp_amount, 0.0001).on()

        self.l_dragon_end = Listener("dragon_end", self.a1_dragon_end)
        self.s2.set_enabled(False)

        self.soul_charge = 0

        self.oblivion_overload = 0
        self.oblivion_overload_timer = Timer(self.add_oblivion_overload)
        self.oblivion_overload_att = Modifier("oo_att", "att", "buff", 0.0)
        self.oblivion_overload_crit = Modifier("oo_cc", "crit", "chance", 0.0)
        self.oblivion_overload_sd = Modifier("oo_sd", "s", "buff", 0.0)

    def set_hp(self, hp, **kwargs):
        if self.soul_charge:
            self._hp = self.max_hp
            return 0
        super().set_hp(hp, **kwargs)

    def add_oblivion_overload(self, t=None):
        self.oblivion_overload += 1
        if self.oblivion_overload < 3:
            self.oblivion_overload_timer.on(20)
        if self.oblivion_overload == 1:
            self.oblivion_overload_att.mod_value = 0.1
        elif self.oblivion_overload == 2:
            self.oblivion_overload_att.mod_value = 0.15
            self.oblivion_overload_crit.mod_value = 0.15
        elif self.oblivion_overload == 2:
            self.oblivion_overload_att.mod_value = 0.2
            self.oblivion_overload_crit.mod_value = 0.2
            self.oblivion_overload_sd.mod_value = 0.2

    def a1_dragon_end(self, e):
        self.s2.set_enabled(True)
        self.add_oblivion_overload()

    def s2_proc(self, e):
        if self.soul_charge < 3:
            self.soul_charge = 3
            self.current_s["s1"] = "mode2"
            self.current_s["s2"] = "mode2"


variants = {None: Gala_Nedrick}
