from core.advbase import *
from module.template import StanceAdv


class Lazry(StanceAdv):
    def prerun(self):
        self.config_stances(
            {
                "low": ModeManager(group="low", s1=True, s2=True),
                "high": ModeManager(group="high", s1=True, s2=True),
            },
            hit_threshold=0,
        )


class Lazry_70MC(Lazry):
    comment = "70MC"
    SAVE_VARIANT = False
    conf = {
        "c": {
            "name": "Lazry",
            "icon": "110355_01_r05",
            "att": 618,
            "hp": 893,
            "ele": "water",
            "wt": "axe",
            "spiral": True,
            "a": [["k_frostbite", 0.3], ["affres_burn", 100.0], ["resself_burn_att", 0.15, 10.0, 15.0], ["s", 0.35, "hp70"]],
        },
        "s1_high": {
            "sp": 3194,
            "startup": 0.1,
            "recovery": 1.56667,
            "attr": [{"dmg": 1.8, "iv": 0.23333}, {"dmg": 1.8, "iv": 0.33333}, {"dmg": 1.8, "iv": 0.56667}, {"dmg": 1.8, "iv": 0.76667}, {"dmg": 10.2, "iv": 1.06667}, {"buff": ["next", 0.2, 1, "s", "buff", "-refresh"], "iv": 1.53333}],
        },
        "s1_low": {"sp": 3194, "startup": 0.1, "recovery": 1.7, "attr": [{"dmg": 3.2, "afflic": ["frostbite", 120, 0.41], "iv": 0.6}, {"dmg": 3.2, "iv": 0.8}, {"dmg": 6.0, "iv": 1.43333}]},
        "s2_high": {"sp": 7475, "startup": 0.1, "recovery": 2.5, "attr": [{"dmg": 4.5, "dispel": 100, "iv": 1.66667}, {"dmg": 16.6, "iv": 1.66667}, {"sp": [1.0, "%", "s1"], "iv": 2.4}]},
        "s2_low": {
            "sp": 7475,
            "startup": 0.1,
            "recovery": 1.66667,
            "attr": [{"buff": ["team", 0.15, 15.0, "att", "buff"], "iv": 1.33333}, {"buff": ["team", 0.1, 15.0, "crit", "chance"], "iv": 1.33333}, {"buff": ["team", 0.03, -1, "maxhp", "buff"], "coei": 1, "iv": 1.33333}],
        },
    }

    def prerun(self):
        super().prerun()
        Event("s").listener(self.a1_amp)
        Event("ds").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(max_level=2)


variants = {None: Lazry, "70MC": Lazry_70MC}
