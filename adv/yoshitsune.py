from core.advbase import *


class Yoshitsune(Adv):
    comment = "no counter on s1/dodge"

    def prerun(self):
        self.allow_dodge = False


class Yoshitsune_COUNTER(Yoshitsune):
    comment = "always counter on s1/dodge"

    def prerun(self):
        super().prerun()
        self.conf.s1.attr = self.conf.s1.attr_counter
        self.allow_dodge = True


variants = {None: Yoshitsune, "COUNTER": Yoshitsune_COUNTER}
