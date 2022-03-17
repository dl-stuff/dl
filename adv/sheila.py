from core.advbase import *


class Sheila(Adv):
    def prerun(self):
        self.evils_bane = Debuff("evils_bane", 0.2, 15, 1, "dummy", source="s1")
        self.evils_bane_modifier = Modifier("evils_bane", "crit", "damage", 0.2, get=self.evils_bane.get)
        self.evils_bane_modifier.on()
        self.s2_crit_mod = None
        self.buff2117 = 1

    def s1_hit2(self, *args):
        # unclear if this is how it works
        if self.evils_bane.timeleft() < 15:
            self.evils_bane.on(15)

    def s1_enhanced_hit3(self, *args):
        self.evils_bane.on(30)

    def s2_before(self, e):
        self.s2_crit_mod = None
        if self.evils_bane.get():
            self.s2_crit_mod = Modifier(e.name, "crit", "chance", 1).off()
            self.extra_actmods.append(self.s2_crit_mod)

    def s2_proc(self, e):
        if self.s2_crit_mod is not None:
            self.extra_actmods.remove(self.s2_crit_mod)


variants = {None: Sheila}
