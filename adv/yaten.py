from lark.tree import Tree
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


class Yaten_70MC(Yaten):
    comment = "70MC"
    conf = {
        "c": {
            "name": "Yaten",
            "icon": "110325_01_r05",
            "att": 606,
            "hp": 902,
            "ele": "shadow",
            "wt": "sword",
            "spiral": True,
            "a": [
                ["estat_att", 3],
                ["estat_crit", 3],
                ["affres_paralysis", 100.0],
                ["resself_paralysis_att", 0.15, 10.0, 15.0],
                ["prep", 100.0],
                ["energized_att", 0.2],
            ],
        },
        "s1": {
            "sp": 2818,
            "startup": 0.0,
            "recovery": 2.36667,
            "attr": [{"dmg": 4.85, "iv": 0.33333}, {"dmg": 4.85, "iv": 0.63889}, {"dmg": 4.85, "iv": 0.83333}, {"dmg": 4.85, "iv": 1.0}, {"buff": ["energy", 1], "iv": 1.75}],
        },
        "s1_energized": {
            "sp": 2818,
            "startup": 0.0,
            "recovery": 1.6,
            "attr": [
                {"dmg": 4.85, "iv": 0.33333},
                {"dmg": 4.85, "iv": 0.63889},
                {"dmg": 4.85, "iv": 0.83333},
                {"dmg": 4.85, "iv": 1.0},
                {"dmg": 1.59, "afflic": ["shadowblight", 120, 0.41], "iv": 1.1, "msl": 0.13333},
                {"dmg": 1.59, "iv": 1.16667, "msl": 0.13333},
                {"dmg": 1.59, "iv": 1.23333, "msl": 0.13333},
                {"dmg": 1.59, "iv": 1.26667, "msl": 0.13333},
                {"dmg": 1.59, "iv": 1.3, "msl": 0.13333},
                {"dmg": 1.59, "iv": 1.33333, "msl": 0.13333},
            ],
        },
        "s2": {
            "sp": 3636,
            "startup": 0.0,
            "recovery": 1.0,
            "attr": [{"amp": ["20000", 2, 0], "ab": 1, "cd": 30.0}, {"buff": ["energy", 2, "team"], "iv": 0.13333}, {"buff": ["team", 35.0, 15.0, "heal", "buff"], "coei": 1, "iv": 0.13333}],
        },
    }

    def prerun(self):
        super().prerun()
        self.s2_up_s1 = False

    def s1_downgrade(self, e):
        if not self.s2_up_s1:
            super().s1_downgrade(e)

    def s1_proc(self, e):
        if e.group == "energized":
            self.s2_up_s1 = False
        super().s1_proc(e)

    def s2_proc(self, e):
        self.s2_up_s1 = True
        self.current_s["s1"] = "energized"
        # if not self.is_set_cd("s2", 30):
        #     self.add_amp(amp_id="20000", max_level=2)


variants = {None: Yaten, "70MC": Yaten_70MC}
