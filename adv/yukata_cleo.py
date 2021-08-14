from core.advbase import *


class Yukata_Cleo(Adv):
    def prerun(self):
        self.a1_mod = Modifier("festival_fever", "ex", "actdown", 0.0)
        self.a1_mod.get = self.a1_get
        Event("amp").listener(self.a3_proc)

    def a1_get(self):
        return 0.05 + 0.05 * len([b for b in self.all_buffs if type(b) == Debuff and b.get() and b.is_zone])

    def a3_proc(self, e):
        if e.source.amp_type == 3:
            self.charge_p("a3", 0.1)


variants = {None: Yukata_Cleo}
