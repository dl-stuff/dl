from conf import DEFAULT
from core.advbase import *


class Ayaha_and_Otoha(Adv):
    def prerun(self):
        self.playtime_stacks = []
        self.playtime_timer = Timer(self.add_playtime, 9, True).on()
        Listener("selfaff", self.reset_playtime).on()

        self.a2_affres = Modifier("a2", "affres", "all", 20)
        self.a2_affres.get = self.a2_affres_get
        self.s1_count = 0
        Listener("s", self.a2_amp).on()

    @property
    def ayaha(self):
        return self.current_s["s1"] == DEFAULT

    @property
    def otoha(self):
        return self.current_s["s1"] == "otoha"

    def add_playtime(self, t):
        self.playtime_stacks.append(
            MultiBuffManager(
                "playtime",
                [
                    Selfbuff("playtime_att", 0.05, -1, "att", "buff", "a3"),
                    Selfbuff("playtime_rcv", 0.1, -1, "recovery", "buff", "a3"),
                ],
                -1,
            )
        )
        if len(self.playtime_stacks) == 3:
            self.playtime_timer.off()

    def reset_playtime(self, e):
        for buff in self.playtime_stacks:
            buff.off()
        self.playtime_stacks = []
        self.playtime_timer.on()

    def s1_proc(self, e):
        self.s1_count += 1
        if self.ayaha:
            self.current_x = "otoha"
            self.current_s["s1"] = "otoha"
            self.current_s["s2"] = "otoha"
        else:
            self.current_x = DEFAULT
            self.current_s["s1"] = DEFAULT
            self.current_s["s2"] = DEFAULT

    def a2_affres_get(self):
        return min(100, 20 * self.s1_count)

    def a2_amp(self, e):
        if e.base in ("s1", "s2") and not self.is_set_cd("a2", 8):
            self.add_amp(amp_id="10000", max_level=1)


variants = {None: Ayaha_and_Otoha}
