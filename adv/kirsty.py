from core.advbase import *


class Kirsty(Adv):
    def prerun(self):
        if not self.nihilism and self.condition("maintain Dauntless Strength"):
            Timer(self.dauntless_strength).on(15)
            Timer(self.dauntless_strength).on(30)
            Timer(self.dauntless_strength).on(45)

    def dauntless_strength(self, t):
        Selfbuff("dauntless_strength", 0.20, -1).on()


class Kirsty_70MC(Kirsty):
    comment = "70MC"
    conf = {
        "c": {
            "name": "Kirsty",
            "icon": "110353_01_r05",
            "att": 610,
            "hp": 900,
            "ele": "wind",
            "wt": "lance",
            "spiral": True,
            "a": [["affres_bog", 100.0], ["resself_bog_att", 0.15, 10.0, 15.0], ["affself_poison_spd_buff", 0.1, 15.0, 15.0], ["k_poison", 0.3]],
        },
        "s1": {
            "sp": 2930,
            "startup": 0.0,
            "recovery": 1.5,
            "attr": [{"dmg": 9.5, "afflic": ["poison", 120, 0.582], "iv": 0.4}, {"dispel": 100, "iv": 0.4}],
        },
        "s2": {
            "sp": 8534,
            "startup": 0.0,
            "recovery": 1.0,
            "attr": [{"amp": ["10000", 2, 0], "cd": 30.0}, {"buff": ["team", 0.2, 15.0, "att", "buff"], "iv": 0.13333}],
        },
    }

    def prerun(self):
        if self.condition("maintain Grand Strategist"):
            Timer(self.dauntless_strength).on(10)
            Timer(self.dauntless_strength).on(20)
            Timer(self.dauntless_strength).on(30)

    def dauntless_strength(self, t):
        Selfbuff("grand_strategist", 0.25, -1).on()
        AffEdgeBuff("grand_strategist_affedge", 0.2, -1, "poison").on()


variants = {None: Kirsty, "70MC": Kirsty_70MC}
