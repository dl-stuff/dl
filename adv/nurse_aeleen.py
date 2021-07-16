from core.advbase import *


class Nurse_Aeleen_70MC(Adv):
    SAVE_VARIANT = False
    conf = {
        "c": {
            "name": "Nurse Aeleen",
            "icon": "110029_02_r04",
            "att": 542,
            "hp": 940,
            "ele": "water",
            "wt": "staff",
            "spiral": True,
            "a": [["prep", 100.0], ["affres_stun", 100.0], ["resself_stun_att", 0.15, 10.0, 15.0], ["sp", 0.04], ["sp", 0.04], ["sp", 0.02]],
        },
        "s1": {
            "sp": 7888,
            "startup": 0.1,
            "recovery": 1.8,
            "attr": [
                {
                    "amp": ["10000", 2, 0],
                    "cd": 30.0,
                },
                {"heal": [44, "team"], "buff": ["team", 35.0, 15.0, "heal", "buff"], "coei": 1, "iv": 0.93333},
                {"buff": ["team", 0.08, 60.0, "att", "buff", "-overwrite_8"], "iv": 0.96667},
                {"buff": ["team", 0.15, 10.0, "defense", "buff"], "iv": 1.0},
            ],
            "energizable": True,
        },
        "s2": {
            "sp": 11832,
            "startup": 0.1,
            "recovery": 1.93333,
            "attr": [{"heal": [108, "team"], "iv": 0.96667}, {"buff": ["nearby", 0.05, -1, "maxhp", "buff"], "coei": 1, "iv": 1.0}],
            "energizable": True,
        },
    }


variants = {None: Adv, "70MC": Nurse_Aeleen_70MC}
