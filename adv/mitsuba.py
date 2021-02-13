from core.advbase import *
from module.template import StanceAdv


class Mitsuba(StanceAdv):
    def prerun(self):
        self.config_stances(
            {
                "sashimi": ModeManager(group="sashimi", x=True, s1=True, s2=True),
                "tempura": ModeManager(group="tempura", x=True, s1=True, s2=True),
            },
            hit_threshold=20,
        )


variants = {None: Mitsuba}
