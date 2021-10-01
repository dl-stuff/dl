from core.advbase import *


class Gala_Elisanne(Adv):
    comment = "70MC"

    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()
        self.divine_revelation = Selfbuff("divine_revelation", 1, 13, "kb", "res", source="a1")
        self.ahits = 0
        Event("fs").listener(self.dr_proc)
        Event("s").listener(self.dr_proc)
        Event("ds").listener(self.dr_proc)

    def dr_proc(self, e):
        self.divine_revelation.on()

    def add_combo(self, name="#"):
        result = super().add_combo(name)
        a_hits = self.hits // 10
        if a_hits > 0 and a_hits != self.ahits:
            self.ahits = a_hits
            self.divine_revelation.on()
        return result

    def s2_autocharge(self, t):
        if self.divine_revelation.get():
            log("sp", "s2_autocharge", 960)
            self.s2.charge(960)  # 2496 - 1536
        elif self.s2.charged < self.s2.sp:
            self.s2.charge(-1536)


class Gala_Elisanne_50MC(Gala_Elisanne):
    SAVE_VARIANT = False
    comment = "50MC"
    conf = {
        "c": {
            "name": "Gala Elisanne",
            "icon": "100002_13_r05",
            "att": 516,
            "hp": 745,
            "ele": "water",
            "wt": "axe",
            "spiral": False,
            "a": [["affres_burn", 100.0], ["affres_stun", 100.0], ["primed_att", 0.1]],
        },
        "s1": {
            "sp": 4377,
            "startup": 0.1,
            "recovery": 1.23333,
            "attr": [
                {"buff": ["ele", 0.3, 15.0, "att", "buff", "water"], "iv": 0.5}
            ],
        },
        "s2": {
            "sp": 38400,
            "startup": 0.1,
            "recovery": 2.06667,
            "attr": [
                {"dmg": 13.431, "iv": 0.2},
                {"dmg": 13.431, "iv": 0.53333},
                {"dmg": 13.431, "iv": 1.43333},
                {"buff": ["energy", 3], "iv": 1.43333},
            ],
        },
    }


variants = {None: Gala_Elisanne, "50MC": Gala_Elisanne_50MC}
