from core.advbase import *
from module.template import StanceAdv, RngCritAdv


class Valerio(StanceAdv, RngCritAdv):
    def prerun(self):
        self.config_stances(
            {
                "appetizer": ModeManager(group="appetizer", x=True, s1=True, s2=True),
                "entree": ModeManager(group="entree", x=True, s1=True, s2=True),
                "dessert": ModeManager(group="dessert", x=True, s1=True, s2=True),
            },
            hit_threshold=20,
        )

        self.config_rngcrit(cd=10, ev=20)
        self.a1_buff = Selfbuff("a1", 0, 20, "spd", "buff")
        self.a1_stack = 0
        if self.MC is None:
            Event("s").listener(self.a1_amp)

    def a1_amp(self, e):
        if not self.is_set_cd("a1_amp", 10):
            self.add_amp(max_level=2)

    def rngcrit_cb(self, mrate=None):
        if self.nihilism:
            return
        new_value = 0.10 * mrate
        if not self.a1_buff:
            self.a1_buff.set(new_value)
            self.a1_buff.on()
        else:
            self.a1_buff.value(new_value)
        self.a1_stack = mrate - 1

    @property
    def buffcount(self):
        buffcount = super().buffcount
        return buffcount + self.a1_stack


class Valerio_RNG(Valerio):
    def prerun(self):
        self.config_stances(
            {
                "appetizer": ModeManager(group="appetizer", x=True, s1=True, s2=True),
                "entree": ModeManager(group="entree", x=True, s1=True, s2=True),
                "dessert": ModeManager(group="dessert", x=True, s1=True, s2=True),
            },
            hit_threshold=20,
        )
        self.config_rngcrit(cd=10)

    def rngcrit_cb(self):
        Selfbuff("a1", 0.10, 20, "spd", "buff").on()


variants = {None: Valerio, "RNG": Valerio_RNG}
