from core.advbase import *


class Kimono_Elisanne(Adv):
    def prerun(self):
        self.ny_buff = MultiLevelBuff(
            "ny_prayer",
            [
                ElementalTeambuff("ny_prayer_lv1", 0.15, 15, "att", "buff", "flame"),
                ElementalTeambuff("ny_prayer_lv2", 0.25, 30, "att", "buff", "flame"),
                ElementalTeambuff("ny_prayer_lv3", 0.40, 60, "att", "buff", "flame"),
            ],
        )
        self.ny_haste = Modifier("a1_haste", "sp", "passive", 0).on()
        self.ny_haste.get = self.get_a1_haste
        self.s2_autocharge = self.s2.autocharge_init(276)

    def get_a1_haste(self):
        return {0: 0, 1: 0.07, 2: 0.08, 3: 0.1}[self.ny_buff.level]

    @allow_acl
    def s(self, n, s1_lv=None):
        if self.in_dform():
            return False
        if n == 1:
            s1_lv = max(1, min(3, s1_lv or 1))
            self.current_s["s1"] = f"lv{s1_lv}"
        return super().s(n)

    def s1_proc(self, e):
        try:
            add_lv = min(4 - self.ny_buff.level, int(e.group[-1]))
        except ValueError:
            add_lv = 1
        for _ in range(add_lv):
            self.ny_buff.on()
        if self.ny_buff.level == 3:
            self.s2_autocharge.on()
        else:
            self.s2_autocharge.off()


variants = {None: Kimono_Elisanne}
