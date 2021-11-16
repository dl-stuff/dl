from core.advbase import *


class Lapis(Adv):
    def prerun(self):
        self.bullets = []
        self.bullet_c = 0
        self.s1_res_down = Debuff("s1_res_down", 0.05, 30, 1, "water_resist", "down", source="s1")

    def add_bullet(self):
        if self.nihilism:
            return
        if len(self.bullets) < 3:
            self.bullets.append(Selfbuff("bullets", 0.04, -1, "crit", "chance").on())

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        if self.condition("always connect hits") and self.hits // 30 > self.bullet_c:
            self.add_bullet()
            self.bullet_c = self.hits // 30
        return result

    def s1_proc(self, e):
        if e.name == "s1" and self.condition("always s1 dispel"):
            self.s1_res_down.on()
            self.add_bullet()

    def s2_before(self, e):
        mod_value = min(0.8, self.buffcount * 0.05 + self.stronger_bullets * 0.15)
        log(
            "s2_mod",
            mod_value,
            (self.buffcount - self.stronger_bullets) * 0.05,
            self.stronger_bullets * 0.20,
        )
        self.s2_bufc_mod = Modifier(e.name, "att", "bufc", mod_value).off()
        self.extra_actmods.append(self.s2_bufc_mod)

    def s2_proc(self, e):
        self.extra_actmods.remove(self.s2_bufc_mod)
        for b in self.bullets:
            b.off()
        self.bullets = []

    @property
    def stronger_bullets(self):
        return len(self.bullets)


variants = {None: Lapis}
