from core.advbase import *


class Pecorine(Adv):
    def prerun(self):
        self.gourmand_gauge = 0
        self.gourmand_mode = ModeManager(group="gourmand", fs=True, s1=True, duration=20, pause=("s", "dragon"))

    def a1_update(self, gauge):
        if not self.gourmand_mode.get():
            self.gourmand_gauge += gauge
            if self.gourmand_gauge == 100:
                self.gourmand_mode.on()
                self.gourmand_gauge = 0

    def hitattr_make(self, name, base, group, aseq, attr, onhit=None):
        self.a1_update(attr.get("cp", 0))
        super().hitattr_make(name, base, group, aseq, attr, onhit=onhit)


variants = {None: Pecorine}
