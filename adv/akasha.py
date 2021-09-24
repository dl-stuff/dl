from core.advbase import *


class Akasha(Adv):
    S2_DURATION = 10

    def prerun(self):
        self.team_sp = 0

    def s2_charge_sp(self, t):
        self.charge(t.name, 420)
        self.team_sp += 420

    def s2_proc(self, e):
        if self.nihilism:
            return
        charge_timer = Timer(self.s2_charge_sp, 1.5, True)
        charge_timer.name = e.name
        EffectBuff("sp_regen_zone", self.S2_DURATION, lambda: charge_timer.on(), lambda: charge_timer.off()).no_bufftime().on()

    def post_run(self, end):
        # self.stats.append(f'team_sp:{self.team_sp}')
        self.comment = f"total {self.team_sp} SP to team from s2"


class Akasha_70MC(Akasha):
    SAVE_VARIANT = False
    S2_DURATION = 15
    conf = {
        "c": {
            "name": "Akasha",
            "icon": "110341_01_r05",
            "att": 561,
            "hp": 967,
            "ele": "wind",
            "wt": "staff",
            "spiral": True,
            "a": [["prep", 100.0], ["affres_bog", 100.0], ["resself_bog_att", 0.15, 10.0, 15.0], ["rcv", 0.17, "hp70"]],
        },
        "s1": {
            "sp": 5916,
            "startup": 0.1,
            "recovery": 1.8,
            "attr": [
                {"heal": [44, "team"], "buff": ["team", 35.0, 15.0, "heal", "buff"], "coei": 1, "iv": 0.93333},
                {"buff": ["team", 0.15, 60.0, "att", "buff", "-overwrite_MYSELF8"], "iv": 0.93333},
                {"buff": ["echo", 0.5, 30.0, "-refresh"], "coei": 1, "iv": 0.93333},
            ],
            "energizable": True,
        },
        "s2": {"sp": 15000, "startup": 0.1, "recovery": 1.96667, "attr": [{"dmg": 9.0, "hp": 100.0, "afflic": ["stormlash", 120, 0.41]}]},
    }

    def prerun(self):
        super().prerun()
        Event("s").listener(self.a1_amp)
        Event("ds").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 30):
            self.add_amp(max_level=2)

    def post_run(self, end):
        try:
            average_echo_att = self.sum_echo_att / g_logs.counts["s"]["s1"]
            self.comment += f"; {average_echo_att:.2f} avg overdamage att"
        except (KeyError, AttributeError):
            pass


variants = {None: Akasha, "70MC": Akasha_70MC}
