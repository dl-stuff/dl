from core.advbase import *


class Cecile(Adv):
    def prerun(self):
        self.manachew_gauge = 0
        self.manachew_mode = ModeManager(
            group="manachew",
            buffs=[Selfbuff("manachew_defense", 0.2, -1, "defense", "passive"), Selfbuff("manachew_sd", 0.1, -1, "s", "passive"), Selfbuff("manachew_sp", 0.08, -1, "sp", "passive")],
            fs=True,
            s1=True,
            s2=True,
            duration=20,
            pause=("s", "dragon"),
        )
        Event("dragon_end").listener(self.dshift_manachew_gauge)

    def a1_update(self, gauge):
        if self.manachew_mode.get():
            max_add = self.manachew_mode.duration - self.manachew_mode.timeleft()
            add_time = min(gauge / 10000 * self.manachew_mode.duration, max_add)
            self.manachew_mode.add_time(add_time)
        else:
            self.manachew_gauge += gauge
            if self.manachew_gauge == 10000:
                self.manachew_mode.on()
                self.manachew_gauge = 0

    def dshift_manachew_gauge(self, e):
        self.a1_update(5000)

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None, dtype=None):
        self.a1_update(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit, dtype=dtype)

    def a1_add_manachew_time(self):
        self.manachew_mode.add_time(2)

    def a3_dodge_gauge_fill(self):
        self.charge_p("a3", 0.2, target="s1")
        self.charge_p("a3", 0.2, target="s2")


class Cecile_DODGE(Cecile):
    def prerun(self):
        super().prerun()
        Event("dodge").listener(self.a1_a3_dodge)
        self.comment = "enable a1/a3 dodge every 15 seconds"

    def a1_a3_dodge(self, e):
        if not self.is_set_cd("a1_a3", 15):
            self.a3_dodge_gauge_fill()
            if self.manachew_mode.get():
                self.a1_add_manachew_time()


variants = {None: Cecile, "DODGE": Cecile_DODGE}
