from core.advbase import *


class Summer_Verica(Adv):
    def prerun(self):
        self.s2.autocharge_init(self.s2_autocharge).on()

    def s2_autocharge(self, t):
        if self.s1.sp > self.s1.charged:
            log("sp", "s2_autocharge", 1578)
            self.s2.charge(1578)


class Summer_Verica_70MC(Summer_Verica):
    SAVE_VARIANT = False
    conf = {
        "c": {
            "name": "Summer Verica",
            "icon": "110269_02_r05",
            "att": 563,
            "hp": 964,
            "ele": "shadow",
            "wt": "staff",
            "spiral": True,
            "a": [["rcv", 0.25, "hp100"], ["prep", 100.0], ["a", 0.15, "hp100"], ["affres_blind", 100.0], ["resself_blind_att", 0.15, 10.0, 15.0], ["rcv", 0.15]],
        },
        "s1": {
            "sp": 5916,
            "startup": 0.0,
            "recovery": 1.8,
            "attr": [
                {"heal": [44, "team"], "buff": ["team", 35.0, 15.0, "heal", "buff"], "coei": 1, "iv": 0.93333},
                {"buff": ["echo", 0.5, 30.0, "-refresh"], "coei": 1, "iv": 0.93333},
                {"buff": ["team", 0.08, 60.0, "att", "buff", "-overwrite_MYSELF8"], "iv": 0.96667},
            ],
            "energizable": True,
        },
        "s2": {
            "sp": 63104,
            "startup": 0.0,
            "recovery": 1.93333,
            "attr": [
                {"amp": ["10000", 2, 0], "cd": 30.0},
                {"buff": ["drain", 0.05, 30.0], "coei": 1, "iv": 0.96667},
            ],
        },
    }

    def post_run(self, end):
        try:
            average_echo_att = self.sum_echo_att / g_logs.counts["s"]["s1"]
            self.comment += f"; {average_echo_att:.2f} avg overdamage att"
        except (KeyError, AttributeError):
            pass


variants = {None: Summer_Verica, "70MC": Summer_Verica_70MC}
