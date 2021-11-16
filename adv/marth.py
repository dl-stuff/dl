from core.advbase import *


class Marth(Adv):
    LAST_BOOST_HEAL_TO = 30
    comment = "team last boost not considered"

    def prerun(self):
        self.a1_proc_chances = 2
        self.last_boost_listener = Listener("hp", self.a1_last_boost)
        if "hp" not in self.conf and self.condition("last boost once at start"):
            Timer(self.lo_damaged).on(0.1)

    def a1_last_boost(self, e):
        if self.a1_proc_chances > 0 and e.hp <= 30 and (e.hp - e.delta) > 30 and not self.is_set_cd("last_boost", 15):
            self.a1_proc_chances -= 1
            self.charge_p("a1_last_boost", 1.0)
            if self.a1_proc_chances == 0:
                self.last_boost_listener.off()

    def lo_damaged(self, t):
        if self.hp > 30 and self.a1_proc_chances > 0:
            next_hp = self.condition.hp_threshold_list()
            if next_hp and next_hp[0] < 30:
                self.set_hp(next_hp)
            else:
                self.set_hp(30)
            Timer(self.lo_healed).on(15)

    def lo_healed(self, t):
        next_hp = self.condition.hp_threshold_list(self.LAST_BOOST_HEAL_TO)
        try:
            self.set_hp(next_hp[0])
        except:
            self.set_hp(100)


variants = {None: Marth}
