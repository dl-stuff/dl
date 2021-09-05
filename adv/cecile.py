from core.advbase import *


class Cecile(Adv):
    def prerun(self):
        self.manachew_gauge = 0
        self.manachew_mode = ModeManager(
            group="manachew",
            buffs=[
                Selfbuff("manachew_defense", 0.2, -1, "defense", "passive"),
                Selfbuff("manachew_sd", 0.1, -1, "s", "passive"),
                Selfbuff("manachew_sp", 0.08, -1, "sp", "passive")],
            fs=True,
            s1=True,
            s2=True,
            duration=20,
            pause=("s", "dragon")
        )
        Event("dragon_end").listener(self.dshift_manachew_gauge)

    def a1_update(self, gauge):
        if not self.manachew_mode.get():
            self.manachew_gauge += gauge
            if self.manachew_gauge == 10000:
                self.manachew_mode.on()
                self.manachew_gauge = 0

    def dshift_manachew_gauge(self, e):
    # wait can you dshift during manachew to add time? todo: figure that out
        self.a1_update(5000)

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.a1_update(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)

    # unused
    def a1_add_manachew_time(self):
        self.manachew_mode.add_time(2)

    # unused
    def a3_dodge_gauge_fill(self):
        self.charge_p("a3", 0.2, target="s1")
        self.charge_p("a3", 0.2, target="s2")


variants = {None: Cecile}
