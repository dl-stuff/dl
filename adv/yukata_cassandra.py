from core.advbase import *


class Yukata_Cassandra(Adv):
    comment = "s1 overdamage team buff not considered"

    def prerun(self):
        self.a3_att_mod = Modifier("a3_att", "att", "passive", 0.30, get=self.a3_get)

    def a3_get(self):
        return self.s2.sp == self.s2.charged

    def post_run(self, end):
        try:
            average_echo_att = self.sum_echo_att / g_logs.counts["s"]["s1"]
            self.comment += f"; {average_echo_att:.2f} avg overdamage att"
        except (KeyError, AttributeError):
            pass


class Yukata_Cassandra_70MC(Yukata_Cassandra):
    SAVE_VARIANT = False
    conf = {
        "c": {
            "name": "Yukata Cassandra",
            "icon": "110337_03_r05",
            "att": 562,
            "hp": 965,
            "ele": "flame",
            "wt": "staff",
            "spiral": True,
            "a": [["prep", 100.0], ["a", 0.2, "hp100"], ["affres_stun", 100.0], ["resself_stun_att", 0.15, 10.0, 15.0], ["a", 0.35]],
        },
        "s1": {"sp": 7734, "startup": 0.0, "recovery": 1.66667, "attr": [{"buff": ["echo", 0.5, 30.0, "-refresh"], "coei": 1, "iv": 1.0}, {"heal": [100, "team"], "iv": 1.0}], "energizable": True},
        "s2": {
            "sp": 13188,
            "startup": 0.0,
            "recovery": 1.93333,
            "attr": [
                {"amp": ["10000", 2, 0], "cd": 30.0},
                {"buff": ["team", 35.0, 20.0, "heal", "buff"], "coei": 1, "iv": 1.0},
            ],
            "energizable": True,
        },
    }

    def prerun(self):
        self.a3_att_mod = Modifier("a3_att", "att", "passive", 0.35, get=self.a3_get)


variants = {None: Yukata_Cassandra, "70MC": Yukata_Cassandra_70MC}
