from core.advbase import *


class Vixel_70MC(Adv):
    SAVE_VARIANT = False
    conf = {
        "c": {
            "name": "Vixel",
            "icon": "110304_01_r04",
            "att": 542,
            "hp": 943,
            "ele": "light",
            "wt": "staff",
            "spiral": True,
            "a": [["rcv", 0.15], ["resself_poison_att", 0.15, 10.0, 15.0], ["resself_sleep_att", 0.15, 10.0, 15.0], ["affres_poison", 100.0], ["affres_sleep", 100.0], ["prep", 100.0], ["scharge_all", 0.05]],
        },
        "fs_vixel": {
            "charge": 0.5,
            "startup": 0.7,
            "recovery": 1.46667,
            "attr": [{"dmg": 0.61, "odmg": 4.2, "sp": 580, "dispel": 100}, {"dmg": 0.61, "odmg": 4.2, "iv": 0.36667}, {"dmg": 0.61, "odmg": 4.2, "iv": 0.73333}, {"dmg": 0.61, "odmg": 4.2, "iv": 0.96667}],
            "interrupt": {"s": 0.0, "dodge": 0.0},
            "cancel": {"s": 0.0, "dodge": 0.0},
        },
        "s1": {
            "sp": 5916,
            "startup": 0.1,
            "recovery": 1.8,
            "attr": [
                {"buff": ["fsAlt", "vixel", -1, 1, "-refresh"], "coei": 1, "ab": 1},
                {"heal": [44, "team"], "buff": ["team", 35.0, 15.0, "heal", "buff"], "coei": 1, "iv": 0.93333},
                {"buff": ["team", 0.15, 60.0, "att", "buff", "-overwrite_MYSELF8"], "iv": 0.96667},
            ],
            "energizable": True,
        },
        "s2": {
            "sp": 4819,
            "startup": 0.1,
            "recovery": 1.96667,
            "attr": [{"amp": ["10000", 2, 0], "cd": 30.0, "ab": 1}, {"heal": [72, "team"], "iv": 1.26667}, {"buff": ["team", 0.1, 10.0, "recovery", "buff"], "coei": 1, "iv": 1.33333}, {"buff": ["energy", 1, "team"], "iv": 1.33333}],
            "energizable": True,
        },
    }


variants = {None: Adv, "70MC": Vixel_70MC}
