from core.advbase import *


class Lea(Adv):
    comment = "s2 self damage counter not implemented"


class Lea_70MC(Lea):
    SAVE_VARIANT = False
    comment = "70MC; " + Lea.comment
    conf = {
        "c": {
            "name": "Lea",
            "icon": "110259_01_r05",
            "att": 605,
            "hp": 904,
            "ele": "flame",
            "wt": "sword",
            "spiral": True,
            "a": [["fs", 0.5], ["k_scorchrend", 0.15], ["affres_stun", 100.0], ["resself_stun_att", 0.15, 10.0, 15.0], ["spf", 0.15]],
        },
        "fs_lea": {
            "startup": 0.14957,
            "recovery": 0.32052,
            "attr": [{"dmg": 1.65, "odmg": 8.0, "sp": 345, "afflic": ["scorchrend", 100, 0.22]}],
        },
        "s1": {
            "sp": 2325,
            "startup": 0.0,
            "recovery": 2.7,
            "attr": [
                {"amp": ["10000", 2, 0], "cd": 30.0},
                {"buff": ["fsAlt", "lea", -1, 1, "-refresh"], "coei": 1},
                {"dmg": 3.3, "killer": [0.5, ["burn"]], "afflic": ["burn", 120, 0.97], "iv": 0.33333},
                {"dispel": 100, "iv": 0.33333},
                {"dmg": 3.3, "killer": [0.5, ["burn"]], "iv": 0.46667},
                {"dmg": 3.3, "killer": [0.5, ["burn"]], "iv": 0.9},
                {"dmg": 3.3, "killer": [0.5, ["burn"]], "iv": 1.16667},
                {"dmg": 3.3, "killer": [0.5, ["burn"]], "iv": 1.96667},
            ],
        },
        "s2": {
            "sp": 4730,
            "startup": 0.0,
            "recovery": 2.13333,
            "attr": [{"hp": -20.0, "cond": ["hp>", 60.0]}, {"dmg": 8.2, "iv": 2.1}, {"dmg": 8.2, "iv": 2.1}],
        },
    }


variants = {None: Adv, "70MC": Lea_70MC}
