from core.advbase import *


class Mitsuhide(Adv):
    def s2_before(self, e):
        # 5: 5
        # 10: 10
        # 15: 15 + 5
        # 20: 20 + 10
        # 25: 25 + 15
        # 30: 30 + 20
        mod = 0
        for i in range(1, 7):
            if self.hits >= i * 5:
                mod += 5
        for i in range(3, 7):
            if self.hits >= i * 5:
                mod += 5
        mod /= 100
        self.s2_combo_mod = Modifier(e.name, "att", "skill_combo", mod).off()
        self.extra_actmods.append(self.s2_combo_mod)

    def s2_proc(self, e):
        self.extra_actmods.remove(self.s2_combo_mod)


variants = {None: Mitsuhide}
