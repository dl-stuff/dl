from core.advbase import *


class Laxi(Adv):
    def prerun(self):
        self.healed = 0
        self.heal = Action("heal", Conf({"startup": 5.0, "recovery": 0.1}))
        self.heal.atype = "s"  # haxx
        Event("hp").listener(self.a1_heal_proc)

    def a1_heal_proc(self, e):
        if self.healed == 0 and e.delta < 0 and e.hp <= 30:
            self.healed = 1
            self.set_hp(100)
            self.heal()
            for buff in self.all_buffs:
                if buff.source != "ability":
                    buff.off()


variants = {None: Laxi}
