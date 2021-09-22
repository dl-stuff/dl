from core.advbase import *


class Gala_Cleo_70MC(Adv):
    SAVE_VARIANT = False
    comment = "70MC"

    conf = {
        "c": {
            "name": "Gala Cleo",
            "icon": "100004_10_r05",
            "att": 586,
            "hp": 942,
            "ele": "shadow",
            "wt": "wand",
            "spiral": True,
            "a": [["resself_blind_att", 0.15, 10.0, 15.0], ["resself_paralysis_att", 0.15, 10.0, 15.0], ["affres_blind", 100.0], ["affres_paralysis", 100.0], ["prep", 100.0], ["rcv", 0.15]],
        },
        "fs_galacleo": {
            "charge": 0.5,
            "startup": 0.0,
            "recovery": 1.0,
            "attr": [{"buff": ["zone", 0.25, 10.0, "att", "buff"], "msl": 0.23333}],
            "interrupt": {"s": 0.0},
            "cancel": {"s": 0.0, "dodge": 0.03333},
        },
        "s1_phase1": {
            "sp": 2814,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0, "ab": 1},
                {"buff": ["fsAlt", "galacleo", -1, 1, "-refresh"], "coei": 1, "ab": 1},
                {"dmg": 0.88},
                {"dmg": 2.7},
                {"dmg": 0.88, "msl": 0.2},
                {"dmg": 2.7, "msl": 0.2},
                {"dmg": 0.88, "msl": 0.4},
                {"dmg": 2.7, "msl": 0.4},
            ],
        },
        "s1_phase2": {
            "sp": 2814,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0, "ab": 1},
                {"buff": ["fsAlt", "galacleo", -1, 1, "-refresh"], "coei": 1, "ab": 1},
                {"dmg": 0.88},
                {"dmg": 2.7},
                {"dmg": 0.88, "msl": 0.15},
                {"dmg": 2.7, "msl": 0.15},
                {"dmg": 0.88, "msl": 0.3},
                {"dmg": 2.7, "msl": 0.3},
                {"dmg": 0.88, "msl": 0.45},
                {"dmg": 2.7, "msl": 0.45},
            ],
            "phase_coei": True,
        },
        "s1_phase3": {
            "sp": 2814,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0, "ab": 1},
                {"buff": ["fsAlt", "galacleo", -1, 1, "-refresh"], "coei": 1, "ab": 1},
                {"dmg": 0.88},
                {"dmg": 2.7},
                {"dmg": 0.88, "msl": 0.1},
                {"dmg": 2.7, "msl": 0.1},
                {"dmg": 0.88, "msl": 0.2},
                {"dmg": 2.7, "msl": 0.2},
                {"dmg": 0.88, "msl": 0.3},
                {"dmg": 2.7, "msl": 0.3},
                {"dmg": 0.88, "msl": 0.4},
                {"dmg": 2.7, "msl": 0.4},
            ],
            "phase_coei": True,
        },
        "s2_phase1": {"sp": 6000, "startup": 0.1, "recovery": 1.5, "attr": [{"dmg": 4.7, "iv": 1.0}, {"buff": ["debuff", -0.1, 20.0, 1.0, "def"], "coei": 1, "iv": 1.0}]},
        "s2_phase2": {
            "sp": 6000,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [{"dmg": 4.7, "iv": 1.0}, {"buff": ["debuff", -0.1, 20.0, 1.0, "def"], "coei": 1, "iv": 1.0}, {"buff": ["debuff", -0.1, 20.0, 1.0, "attack"], "coei": 1, "iv": 1.0}],
            "phase_coei": True,
        },
        "s2_phase3": {
            "sp": 6000,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"dmg": 4.7, "iv": 1.0},
                {"buff": ["debuff", -0.1, 20.0, 1.0, "def"], "coei": 1, "iv": 1.0},
                {"buff": ["debuff", -0.1, 20.0, 1.0, "attack"], "coei": 1, "iv": 1.0},
                {"heal": [22, "team"], "buff": ["team", 17.0, 20.0, "heal", "buff"], "coei": 1, "iv": 1.0},
            ],
            "phase_coei": True,
        },
    }


class Gala_Cleo_52MC(Adv):
    SAVE_VARIANT = False
    comment = "52MC"

    conf = {
        "c": {
            "name": "Gala Cleo",
            "icon": "100004_10_r05",
            "att": 507,
            "hp": 814,
            "ele": "shadow",
            "wt": "wand",
            "spiral": False,
            "a": [["affres_blind", 100.0], ["affres_paralysis", 100.0], ["prep", 100.0]],
        },
        "fs_galacleo": {
            "charge": 0.5,
            "startup": 0.0,
            "recovery": 1.0,
            "attr": [{"buff": ["zone", 0.25, 10.0, "att", "buff"], "msl": 0.23333}],
            "interrupt": {"s": 0.0},
            "cancel": {"s": 0.0, "dodge": 0.03333},
        },
        "s1_phase1": {
            "sp": 2814,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0},
                {"buff": ["fsAlt", "galacleo", -1, 1, "-refresh"], "coei": 1},
                {"dmg": 0.88},
                {"dmg": 2.65},
                {"dmg": 0.88, "msl": 0.2},
                {"dmg": 2.65, "msl": 0.2},
                {"dmg": 0.88, "msl": 0.4},
                {"dmg": 2.65, "msl": 0.4},
            ],
        },
        "s1_phase2": {
            "sp": 2814,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0},
                {"buff": ["fsAlt", "galacleo", -1, 1, "-refresh"], "coei": 1},
                {"dmg": 0.88},
                {"dmg": 2.65},
                {"dmg": 0.88, "msl": 0.15},
                {"dmg": 2.65, "msl": 0.15},
                {"dmg": 0.88, "msl": 0.3},
                {"dmg": 2.65, "msl": 0.3},
                {"dmg": 0.88, "msl": 0.45},
                {"dmg": 2.65, "msl": 0.45},
            ],
            "phase_coei": True,
        },
        "s1_phase3": {
            "sp": 2814,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"amp": ["10000", 3, 0], "cd": 30.0},
                {"buff": ["fsAlt", "galacleo", -1, 1, "-refresh"], "coei": 1},
                {"dmg": 0.88},
                {"dmg": 2.65},
                {"dmg": 0.88, "msl": 0.1},
                {"dmg": 2.65, "msl": 0.1},
                {"dmg": 0.88, "msl": 0.2},
                {"dmg": 2.65, "msl": 0.2},
                {"dmg": 0.88, "msl": 0.3},
                {"dmg": 2.65, "msl": 0.3},
                {"dmg": 0.88, "msl": 0.4},
                {"dmg": 2.65, "msl": 0.4},
            ],
            "phase_coei": True,
        },
        "s2_phase1": {"sp": 6000, "startup": 0.1, "recovery": 1.5, "attr": [{"dmg": 4.6, "iv": 1.0}, {"buff": ["debuff", -0.1, 20.0, 1.0, "def"], "coei": 1, "iv": 1.0}]},
        "s2_phase2": {
            "sp": 6000,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [{"dmg": 4.6, "iv": 1.0}, {"buff": ["debuff", -0.1, 20.0, 1.0, "def"], "coei": 1, "iv": 1.0}, {"buff": ["debuff", -0.05, 20.0, 1.0, "attack"], "coei": 1, "iv": 1.0}],
            "phase_coei": True,
        },
        "s2_phase3": {
            "sp": 6000,
            "startup": 0.1,
            "recovery": 1.4,
            "attr": [
                {"dmg": 4.6, "iv": 1.0},
                {"buff": ["debuff", -0.1, 20.0, 1.0, "def"], "coei": 1, "iv": 1.0},
                {"buff": ["debuff", -0.05, 20.0, 1.0, "attack"], "coei": 1, "iv": 1.0},
                {"heal": [22, "team"], "buff": ["team", 17.0, 15.0, "heal", "buff"], "coei": 1, "iv": 1.0},
            ],
            "phase_coei": True,
        },
    }


variants = {None: Adv, "70MC": Gala_Cleo_70MC, "52MC": Gala_Cleo_52MC}
