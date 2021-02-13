from core.advbase import *


class Yaten(Adv):
    def prerun(self):
        Event("energy").listener(self.s1_upgrade)
        Event("energy_end").listener(self.s1_downgrade)

    def s1_upgrade(self, e):
        if e.stack >= 5:
            log("debug", "upgrade")
            self.current_s["s1"] = "energized"

    def s1_downgrade(self, e):
        log("debug", "downgrade (no energy)")
        self.current_s["s1"] = "default"

    def s1_proc(self, e):
        if e.group == "energized":
            log("debug", "downgrade (s1 proc)")
            self.current_s["s1"] = "default"


variants = {None: Yaten}
