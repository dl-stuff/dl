from core.advbase import *


class Nadine(Adv):
    FIXED_RNG = None

    def prerun(self):
        self.team_s1_hits = 1
        teammates = 2
        if self.condition(f"{teammates} teammates in s1"):
            self.team_s1_hits += teammates

    @staticmethod
    def prerun_skillshare(adv, dst):
        adv.team_s1_hits = 1
        teammates = 2
        if adv.condition(f"{teammates} teammates in {dst}"):
            adv.team_s1_hits += teammates

    def s1_before(self, e):
        # todo: check if overdamage applies to hit counting?
        for _ in range(self.team_s1_hits):
            self.add_combo(e.name)
        aseq = 1 if e.group == "default" else 3 + 1
        s1_hits = 1 if e.group == "default" else 3
        s1_hits += self.team_s1_hits
        log("debug", "s1_hits", s1_hits, self.team_s1_hits)
        if s1_hits == 3:
            self.hitattr_make(e.name, e.base, e.group, aseq, self.conf[e.name].extra_3, dtype=e.dtype)
        elif 4 <= s1_hits <= 5:
            self.hitattr_make(e.name, e.base, e.group, aseq, self.conf[e.name].extra_5, dtype=e.dtype)
        elif s1_hits >= 6:
            self.hitattr_make(e.name, e.base, e.group, aseq, self.conf[e.name].extra_6, dtype=e.dtype)


class Nadine_TREND(Nadine):
    SAVE_VARIANT = False
    FIXED_RNG = True
    comment = "s2 always trending"


class Nadine_NO_TREND(Nadine):
    SAVE_VARIANT = False
    NO_DEPLOY = True
    FIXED_RNG = False
    comment = "s2 never trending"


variants = {None: Nadine, "mass": Nadine, "TREND": Nadine_TREND, "NOTREND": Nadine_NO_TREND}
