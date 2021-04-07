from core.advbase import *


class Gala_Prince(Adv):
    def prerun(self):
        self.s2.autocharge_init(32000).on()
        if self.condition("draconic charge"):
            self.dragonform.dragon_gauge += 500
        Modifier("dragonlight_dt", "dt", "hecc", 1 / 0.7 - 1).on()
        self.dragonform.shift_spd_mod = Modifier("dragonlight_spd", "spd", "buff", 0.10).off()


class Gala_Prince_70MC(Adv):
    comment = "70MC"
    conf = {
        "c": {
            "name": "Gala Prince",
            "icon": "100001_08_r05",
            "att": 602,
            "hp": 908,
            "ele": "light",
            "wt": "sword",
            "spiral": True,
            "a": [
                ["resself_poison_att", 0.15, 10.0, 15.0],
                ["resself_curse_att", 0.15, 10.0, 15.0],
                ["affres_poison", 100.0],
                ["affres_curse", 100.0],
            ],
        },
        "s1": {
            "sp": 3817,
            "startup": 0.1,
            "recovery": 2.4,
            "attr": [{"dmg": 17.0, "iv": 0.8}, {"buff": ["zone", 0.2, 10.0, "att", "buff"], "iv": 0.8}],
        },
        "s2": {
            "sp": 999999,
            "startup": 0.1,
            "recovery": 2.66667,
            "attr": [
                {"dmg": 1.34, "iv": 0.43333},
                {"dmg": 4.0, "iv": 0.5},
                {"dmg": 1.34, "iv": 0.63333},
                {"dmg": 1.34, "iv": 0.8},
                {"dmg": 4.0, "iv": 1.16667},
                {"dmg": 4.0, "iv": 1.43333},
                {"dmg": 4.0, "iv": 1.53333},
                {"dmg": 4.0, "afflic": ["paralysis", 100, 0.803], "iv": 1.66667},
                {"dmg": 4.0, "iv": 1.86667},
                {"dmg": 4.0, "iv": 2.06667},
                {"dmg": 4.0, "iv": 2.2},
                {"dmg": 4.0, "iv": 2.46667},
                {"dmg": 4.0, "iv": 2.46667},
                {"buff": ["team", 0.15, 15.0, "att", "buff"], "iv": 2.6},
                {"buff": ["team", 0.2, 15.0, "defense", "buff"], "iv": 2.6},
                {
                    "amp": [[2, 3, 3, 15.0, "att", "buff"], [[0.03, 60.0], [0.05, 60.0], [0.2, 30.0], [0.4, 30.0], [0.6, 60.0], [0.8, 60.0]]],
                    "iv": 2.6,
                },
            ],
        }
    }

    def prerun(self):
        self.s2.autocharge_init(32000).on()
        if self.condition("draconic charge"):
            self.dragonform.dragon_gauge += 500
        Modifier("dragonlight_dt", "dt", "hecc", 1 / 0.6 - 1).on()
        self.dragonform.shift_spd_mod = Modifier("dragonlight_spd", "spd", "buff", 0.10).off()


variants = {None: Gala_Prince, "70MC": Gala_Prince_70MC}
