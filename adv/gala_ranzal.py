from core.advbase import *

gauge_values = {
    "x1": 77,
    "x2": 77,
    "x3": 100,
    "x4": 136,
    "x5": 200,
    "fs": 150,
    "fs_enhanced": 1000,
}


class Gala_Ranzal(Adv):
    def prerun(self):
        self.gauges = {"x": 0, "fs": 0}

    def charge_gauge(self, source, name):
        self.gauges[source] = min(self.gauges[source] + gauge_values[name], 1000)
        log("gauges", name, f'{self.gauges["x"]}/1000', f'{self.gauges["fs"]}/1000')

    def x_proc(self, e):
        self.charge_gauge("x", e.name)

    def fs_proc(self, e):
        self.charge_gauge("fs", e.name)

    def fs_enhanced_proc(self, e):
        self.charge_gauge("fs", e.name)

    def s1_before(self, e):
        self.s1_boosted_mod = None
        boost = 0
        if self.gauges["x"] >= 1000:
            boost += 1
            self.gauges["x"] = 0
        if self.gauges["fs"] >= 1000:
            boost += 1
            self.gauges["fs"] = 0
        if boost == 0:
            return
        if boost == 1:
            self.s1_boosted_mod = Modifier(e.name, "att", "granzal", 0.15).off()
        elif boost == 2:
            self.s1_boosted_mod = Modifier(e.name, "att", "granzal", 1.0).off()
        if self.s1_boosted_mod:
            self.extra_actmods.append(self.s1_boosted_mod)

    def s1_proc(self, e):
        if self.s1_boosted_mod:
            self.extra_actmods.remove(self.s1_boosted_mod)
            self.s1_boosted_mod = None


class Gala_Ranzal_70MC(Gala_Ranzal):
    SAVE_VARIANT = False
    conf = {
        "c": {
            "name": "Gala Ranzal",
            "icon": "100003_07_r05",
            "att": 604,
            "hp": 905,
            "ele": "wind",
            "wt": "sword",
            "spiral": True,
            "a": [
                ["resself_freeze_att", 0.15, 10.0, 15.0],
                ["resself_bog_att", 0.15, 10.0, 15.0],
                ["affres_freeze", 100.0],
                ["affres_bog", 100.0],
                ["s", 0.35],
            ],
        },
        "fs_enhanced": {
            "startup": 0.25,
            "recovery": 0.66667,
            "attr": [{"dmg": 2.075, "odmg": 3.3, "sp": 330}, {"dmg": 2.075, "odmg": 3.3, "iv": 0.20833}, {"dmg": 2.3, "odmg": 3.3, "iv": 0.5}],
        },
        "s1": {
            "sp": 2661,
            "startup": 0.1,
            "recovery": 1.53846,
            "attr": [
                {"dmg": 3.09, "iv": 0.61538},
                {"dmg": 3.09, "iv": 0.61538, "msl": 0.33333},
                {"dmg": 3.09, "iv": 0.61538, "msl": 0.6},
                {"dmg": 3.09, "iv": 0.61538, "msl": 0.86667},
                {"dmg": 3.09, "iv": 0.61538, "msl": 1.0},
                {"dmg": 3.09, "iv": 0.61538, "msl": 1.2},
            ],
        },
        "s2": {
            "sp": 5800,
            "startup": 0.1,
            "recovery": 1.0,
            "attr": [{"buff": ["fsAlt", "enhanced", -1, 3, "-refresh"], "coei": 1}, {"buff": ["team", 0.2, 15.0, "defense", "buff"], "iv": 0.16667}],
        },
    }

    def prerun(self):
        super().prerun()
        self.s2_timer = Timer(self.s2_cd_end, 30)
        self.s2_cd = False

    def s2_cd_end(self, t):
        self.s2_cd = False

    def s2_proc(self, e):
        if not self.s2_cd:
            # y tho
            self.add_one_att_amp(max=3)
            self.s2_cd = True
            self.s2_timer.on()


variants = {None: Gala_Ranzal, "70MC": Gala_Ranzal_70MC}
