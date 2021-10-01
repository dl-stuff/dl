from core.advbase import *


class Harle(Adv):
    comment = "no counter on s1"

    def prerun(self):
        self.s2_debuff = Selfbuff("crit_vuln", 0.5, 60, "crit").no_bufftime()
        self.team_evasion = 0

    def s2_proc(self, e):
        self.s2_debuff.on()
        self.team_evasion += 2

    def post_run(self, end):
        try:
            self.comment += f"; {self.team_evasion} stacks team evasion"
        except (KeyError, AttributeError):
            pass


class Harle_COUNTER(Harle):
    SAVE_VARIANT = False
    comment = "always max counter on s1"

    def prerun(self):
        super().prerun()
        self.current_s["s1"] = "dodge"


variants = {None: Harle, "COUNTER": Harle_COUNTER}
