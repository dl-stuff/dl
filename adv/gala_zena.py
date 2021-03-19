from core.advbase import *


class Gala_Zena(Adv):
    def prerun(self):
        self.auspex_count = 0
        self.a3_modifier = Modifier("zena_a3", "att", "passive", 0.0)
        self.a3_modifier.get = self.a3_get
        self.fs_alt = FSAltBuff("a1_auspex", "auspex", uses=1)
        # ExAbility hp does not work for A3
        self.passive_hp = self.sub_mod("maxhp", "passive")
        for coab in self.slots.c.coabs.values():
            for ex in coab["ex"]:
                if ex[0] == "hp":
                    self.passive_hp -= ex[1]

    def update_auspex(self):
        if not self.fs_alt.get():
            self.auspex_count += 1
        if self.auspex_count >= 2:
            self.fs_alt.on()
            self.auspex_count = 0

    def s1_proc(self, _):
        self.update_auspex()

    def s2_proc(self, _):
        self.update_auspex()

    def a3_get(self):
        if self.hp > 70:
            return self.passive_hp * ((self.hp - 70) / 30 * 0.5 + 0.5)
        else:
            return self.passive_hp * (self.hp / 70 * 0.4 + 0.1)


variants = {None: Gala_Zena}
