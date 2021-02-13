from core.advbase import *


class Kimono_Elisanne(Adv):
    def override_effect_off(self, buff):
        o_effect_off = buff.effect_off

        def effect_off():
            self.update_ny_level(0)
            o_effect_off()

        buff.effect_off = effect_off

    def prerun(self):
        self.ny_buff = [
            ElementalTeambuff("s1_ny_lv1", 0.15, 15, "att", "buff", "flame"),
            ElementalTeambuff("s1_ny_lv2", 0.25, 30, "att", "buff", "flame"),
            ElementalTeambuff("s1_ny_lv3", 0.40, 60, "att", "buff", "flame"),
        ]
        for buff in self.ny_buff:
            self.override_effect_off(buff)
        self.ny_level = 0
        self.ny_haste = [
            Modifier("a1_haste", "sp", "passive", 0.07),
            Modifier("a1_haste", "sp", "passive", 0.08),
            Modifier("a1_haste", "sp", "passive", 0.10),
        ]
        self.s2_autocharge = self.s2.autocharge_init(276)

    def update_ny_level(self, new_level):
        self.ny_level = new_level
        for i, mod in enumerate(self.ny_haste):
            if i == new_level - 1:
                mod.on()
            elif mod.get():
                mod.off()
        if new_level == 3:
            self.s2_autocharge.on()
        else:
            self.s2_autocharge.off()

    @allow_acl
    def s(self, n, s1_lv=None):
        if n == 1:
            s1_lv = max(1, min(3, s1_lv or 1))
            self.current_s["s1"] = f"lv{s1_lv}"
        return super().s(n)

    def s1_proc(self, e):
        try:
            add_lv = int(e.group[-1])
        except ValueError:
            add_lv = 1
        new_level = min(3, self.ny_level + add_lv)
        for i, buff in enumerate(self.ny_buff):
            if i == new_level - 1:
                buff.on()
            elif buff.get():
                buff.off()
        self.update_ny_level(new_level)


variants = {None: Kimono_Elisanne}
